#/usr/bin/env python3
__doc__ = """ Tool for testing HTD communications """
import argparse
import logging
import socket
import sys


CMD_BASE = [0x02, 0x0]
logger = logging.getLogger('htd_test')

commands = {
    'set_input': {'x': 0x04, 'y': lambda y: 0x03 + y - 1},
    'all_on': {'zone': 0x01, 'x': 0x04, 'y': lambda y: 0x38},
    'all_off': {'zone': 0x01, 'x': 0x04, 'y': lambda y: 0x39},
    'toggle_mute': {'x': 0x04, 'y': lambda y: 0x22},
    'turn_on': {'x': 0x04, 'y': lambda y: 0x20},
    'turn_off': {'x': 0x04, 'y': lambda y: 0x21},
    'state': {'x': 0x06, 'y': lambda y: 0x00, 'response': 0xff}
}

def checksum(s_bytes):
    csum = 0
    for b in s_bytes:
        csum += int(b)
    return csum

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('-L', choices=['DEBUG', 'INFO'], default='INFO',
                        help="Log Level (%(default)s)")
    parser.add_argument('--ip', '-i', type=str, default='172.16.1.133',
                        help="IP address of (W)GW-SL1 gateway")
    parser.add_argument('--cmd', '-c', type=str, choices=commands.keys(),
                        required=True, help='Send command')
    parser.add_argument('--arg', '-a', type=int,
                        help='Command argument')
    parser.add_argument('--zone', '-z', type=int, choices=[1, 2, 3, 4, 5, 6],
                        help='MC-66 zone')

    args = parser.parse_args()

    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.settimeout(5)
    s.connect((args.ip, 10006))

    s_bytes = bytearray()
    for b in CMD_BASE:
        s_bytes.append(b)

    if 'zone' not in commands[args.cmd]:
        s_bytes.append(args.zone)
    else:
        s_bytes.append(commands[args.cmd]['zone'])

    s_bytes.append(commands[args.cmd]['x'])
    s_bytes.append(commands[args.cmd]['y'](args.arg))
    s_bytes.append(checksum(s_bytes))

    ret = s.send(s_bytes)
    if ret != len(s_bytes):
        logger.error("wrote %d of %d bytes", ret, len(s_bytes))
    if 'response' in commands[args.cmd]:
        ret = s.recv(commands[args.cmd]['response'])
        for x in ret:
            sys.stdout.write(hex(x) + ', ')
        sys.stdout.write("\n")
