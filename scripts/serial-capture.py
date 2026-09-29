"""Raw UART capture: open first, then press RST to include the full boot."""
import argparse
from pathlib import Path
import sys
import time
import serial
p = argparse.ArgumentParser()
p.add_argument('port', help='Verified stable /dev/serial/by-id or by-path path')
p.add_argument('--reset', action='store_true', help='Reset through the verified bridge after capture opens')
p.add_argument('--seconds', type=float, default=120)
p.add_argument('--output', default='logs/first_boot.log')
a = p.parse_args()
if not a.port.startswith(('/dev/serial/by-id/', '/dev/serial/by-path/')):
    p.error('Use a verified stable device path, not enumeration order')
uart = serial.Serial(port=None, baudrate=115200, timeout=0.2)
uart.dtr = False
uart.rts = False
uart.port = a.port
uart.open()
try:
    print('Capturing complete ROM + bootloader + app log; reset requested=' + str(a.reset), file=sys.stderr)
    end = time.monotonic() + a.seconds
    with Path(a.output).open('xb') as output:
        if a.reset:
            from esptool.reset import HardReset
            HardReset(uart)()
        while time.monotonic() < end:
            data = uart.read(uart.in_waiting or 1)
            if data:
                output.write(data)
                output.flush()
                sys.stdout.buffer.write(data)
                sys.stdout.buffer.flush()
finally:
    uart.close()
