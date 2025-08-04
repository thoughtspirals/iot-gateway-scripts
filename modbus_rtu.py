from pymodbus.client.serial import ModbusSerialClient as ModbusClient
import time
import os

# Configuration Constants
SLAVE_ID = 181
PORT = 'COM11' if os.name == 'nt' else '/dev/ttyUSB0'
BAUDRATE = 9600
PARITY = 'N'
STOPBITS = 1
BYTESIZE = 8
TIMEOUT = 2
READ_INTERVAL = 5  # seconds between loops

MODBUS_OFFSET = 40001  # Subtract from all register addresses in datasheet

# Register Definitions (from WL-4405 datasheet)
wl4405_registers = [
    {"addr": 40101, "name": "Watts Total", "unit": "W", "scaling": 100},
    {"addr": 40103, "name": "Watts R Phase", "unit": "W", "scaling": 100},
    {"addr": 40105, "name": "Watts Y Phase", "unit": "W", "scaling": 100},
    {"addr": 40107, "name": "Watts B Phase", "unit": "W", "scaling": 100},

    {"addr": 40109, "name": "VAR Total", "unit": "VAR", "scaling": 100},
    {"addr": 40111, "name": "VAR R Phase", "unit": "VAR", "scaling": 100},
    {"addr": 40113, "name": "VAR Y Phase", "unit": "VAR", "scaling": 100},
    {"addr": 40115, "name": "VAR B Phase", "unit": "VAR", "scaling": 100},

    {"addr": 40117, "name": "VA Total", "unit": "VA", "scaling": 100},
    {"addr": 40119, "name": "VA R Phase", "unit": "VA", "scaling": 100},
    {"addr": 40121, "name": "VA Y Phase", "unit": "VA", "scaling": 100},
    {"addr": 40123, "name": "VA B Phase", "unit": "VA", "scaling": 100},

    {"addr": 40125, "name": "PF Total", "unit": "", "scaling": 100},
    {"addr": 40127, "name": "PF R Phase", "unit": "", "scaling": 100},
    {"addr": 40129, "name": "PF Y Phase", "unit": "", "scaling": 100},
    {"addr": 40131, "name": "PF B Phase", "unit": "", "scaling": 100},

    {"addr": 40133, "name": "Frequency", "unit": "Hz", "scaling": 100},

    {"addr": 40135, "name": "Voltage R-N", "unit": "V", "scaling": 100},
    {"addr": 40137, "name": "Voltage Y-N", "unit": "V", "scaling": 100},
    {"addr": 40139, "name": "Voltage B-N", "unit": "V", "scaling": 100},

    {"addr": 40141, "name": "Voltage R-Y", "unit": "V", "scaling": 100},
    {"addr": 40143, "name": "Voltage Y-B", "unit": "V", "scaling": 100},
    {"addr": 40145, "name": "Voltage B-R", "unit": "V", "scaling": 100},

    {"addr": 40147, "name": "Current R", "unit": "A", "scaling": 1000},
    {"addr": 40149, "name": "Current Y", "unit": "A", "scaling": 1000},
    {"addr": 40151, "name": "Current B", "unit": "A", "scaling": 1000},

    {"addr": 40153, "name": "Current Average", "unit": "A", "scaling": 1000},
    {"addr": 40155, "name": "Current Neutral", "unit": "A", "scaling": 1000},

    {"addr": 40157, "name": "VAH", "unit": "VAH", "scaling": 1},
    {"addr": 40159, "name": "VARH", "unit": "VARH", "scaling": 1},
    {"addr": 40161, "name": "WH", "unit": "WH", "scaling": 1},
    {"addr": 40163, "name": "Running Hours", "unit": "hr", "scaling": 1},
]

# Function to read and parse each register
def read_register(client, register, slave=SLAVE_ID):
    modbus_addr = register["addr"] - MODBUS_OFFSET
    try:
        result = client.read_holding_registers(address=modbus_addr, count=2, slave=slave)
        if result.isError():
            return None, f"❌ Modbus Error"
        raw = result.registers[0]
        formatted = f"{raw / register['scaling']:.2f}" if raw != 0 else "0.00"
        return raw, formatted
    except Exception as e:
        return None, f"⚠️ {str(e)}"

# Main loop
def main():
    print("🔌 WL4405 RS-485 Modbus Reader")
    print(f"Port: {PORT} | Baudrate: {BAUDRATE} | Parity: {PARITY} | Slave ID: {SLAVE_ID}")
    print("Press Ctrl+C to stop.\n")

    client = ModbusClient(
        port=PORT,
        baudrate=BAUDRATE,
        parity=PARITY,
        stopbits=STOPBITS,
        bytesize=BYTESIZE,
        timeout=TIMEOUT
    )

    try:
        if not client.connect():
            print(f" Could not connect to {PORT}")
            print(" Ensure WL-4405 is powered and USB-RS485 is connected.")
            return

        print(f"Connected to WL-4405 on {PORT}\n")

        while True:
            print(f" {time.strftime('%Y-%m-%d %H:%M:%S')}")
            print("-" * 50)

            for reg in wl4405_registers:
                raw, value = read_register(client, reg)
                label = f"{reg['name']:<20}"
                if raw is None:
                    print(f"{label}: {value:<25} [{reg['unit']}]")
                else:
                    print(f"{label}: {value:>8} {reg['unit']:<5} (Raw: {raw})")

            print("-" * 50)
            time.sleep(READ_INTERVAL)

    except KeyboardInterrupt:
        print("\n Interrupted by user")

    except Exception as e:
        print(f" Unexpected error: {e}")

    finally:
        if client.is_socket_open():
            client.close()
            print(" Serial connection closed.")

if __name__ == "__main__":
    main()
