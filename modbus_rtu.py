import minimalmodbus
import time

# Constants
SLAVE_ID = 181
PORT = '/dev/ttyAS1'
BAUDRATE = 9600
PARITY = 'N'
STOPBITS = 1
BYTESIZE = 8
TIMEOUT = 2
MODBUS_OFFSET = 40001
READ_INTERVAL = 5  # seconds between loops

# Configure the instrument
instrument = minimalmodbus.Instrument(PORT, SLAVE_ID)
instrument.serial.baudrate = BAUDRATE
instrument.serial.bytesize = 8
instrument.serial.stopbits = 1
instrument.serial.parity   = minimalmodbus.serial.PARITY_EVEN
instrument.serial.timeout  = 1
instrument.mode = minimalmodbus.MODE_RTU

# Register Definitions
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

def main():
    print("🔌 WL4405 RS-485 Reader using minimalmodbus\n")
    try:
        while True:
            print(f"📅 {time.strftime('%Y-%m-%d %H:%M:%S')}")
            print("-" * 50)
            for reg in wl4405_registers:
                try:
                    addr = reg["addr"] - MODBUS_OFFSET
                    value = instrument.read_register(addr, 0, functioncode=3)
                    scaled = value / reg["scaling"]
                    print(f"{reg['name']:<20}: {scaled:.2f} {reg['unit']} (Raw: {value})")
                except Exception as e:
                    print(f"{reg['name']:<20}: ⚠️ {str(e)}")
            print("-" * 50)
            time.sleep(READ_INTERVAL)
    except KeyboardInterrupt:
        print("\nStopped by user.")

if __name__ == "__main__":
    main()
