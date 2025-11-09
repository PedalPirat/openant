from openant.easy.node import Node
from openant.devices import ANTPLUS_NETWORK_KEY
from openant.devices.tire_pressure_monitor import TirePressureMonitor, TirePressureData


def main_dual(front_device_id, rear_device_id):
    node = Node()
    node.set_network_key(0x00, ANTPLUS_NETWORK_KEY)

    front_tpms = TirePressureMonitor(node, device_id=front_device_id)
    rear_tpms = TirePressureMonitor(node, device_id=rear_device_id)

    def make_on_found(device_name):
        def on_found():
            print(f"{device_name} found and receiving")
        return on_found

    def make_on_device_data(device_name):
        def on_device_data(page: int, page_name: str, data):
            if page_name == "tire_pressure" and isinstance(data, TirePressureData):
                print(
                    f"{device_name} - Tire {data.position} pressure: {data.pressure / 1000:.3f} bar; {data.pressure / 68.947573:.1f} psi"
                )
        return on_device_data

    front_tpms.on_found = make_on_found(f"Front tire (ID: {front_device_id})")
    front_tpms.on_device_data = make_on_device_data(f"Front tire (ID: {front_device_id})")
    
    rear_tpms.on_found = make_on_found(f"Rear tire (ID: {rear_device_id})")
    rear_tpms.on_device_data = make_on_device_data(f"Rear tire (ID: {rear_device_id})")

    try:
        print(f"Starting tire pressure monitoring for devices {front_device_id} and {rear_device_id}, press Ctrl-C to finish")
        node.start()
    except KeyboardInterrupt:
        print(f"Closing ANT+ devices...")
    finally:
        front_tpms.close_channel()
        rear_tpms.close_channel()
        node.stop()


def main(device_id=0):
    node = Node()
    node.set_network_key(0x00, ANTPLUS_NETWORK_KEY)

    tpms = TirePressureMonitor(node, device_id=device_id)

    def on_found():
        print(f"Device {tpms} found and receiving")

    def on_device_data(page: int, page_name: str, data):
        if page_name == "tire_pressure" and isinstance(data, TirePressureData):
            print(
                f"Tire {data.position} pressure: {data.pressure / 1000:.3f} bar; {data.pressure / 68.947573:.1f} psi"
            )

    tpms.on_found = on_found
    tpms.on_device_data = on_device_data

    try:
        print(f"Starting {tpms}, press Ctrl-C to finish")
        node.start()
    except KeyboardInterrupt:
        print(f"Closing ANT+ device...")
    finally:
        tpms.close_channel()
        node.stop()


if __name__ == "__main__":
    import sys
    if len(sys.argv) == 3:
        # Two device IDs provided - monitor both
        front_id = int(sys.argv[1])
        rear_id = int(sys.argv[2])
        main_dual(front_id, rear_id)
    elif len(sys.argv) == 2:
        # One device ID provided - monitor single
        device_id = int(sys.argv[1])
        main(device_id)
    else:
        # No arguments - default behavior
        print("Usage:")
        print("  python tire_pressure_monitor.py <device_id>                    # Monitor single device")
        print("  python tire_pressure_monitor.py <front_id> <rear_id>           # Monitor both devices")
        print("  python tire_pressure_monitor.py                                # Monitor device 0 (default)")
        print("")
        print("Your devices found by scanner:")
        print("  Front tire: 22789")
        print("  Rear tire: 21686")
        print("")
        print("Example: python tire_pressure_monitor.py 22789 21686")
        main(0)
