#!/usr/bin/env python
#
# Copyright (c) 2022 Hanson Robotics.
#
# This file is part of Hanson AI.
# See https://www.hansonrobotics.com/hanson-ai for further info.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#

import argparse
import json
from pprint import pprint as pp
from serial.tools.list_ports import grep as grep_serial_ports
import scservo_sdk as sdk

ACTIONS = {
    'reset_neutral':
        {
            'addr':     40,
            'length':   1,
            'write':    128
        },
    'id':
        {
            'addr':     5,
            'length':   1,
        }
}

def argument_parser():
    parser = argparse.ArgumentParser(description="Read Write Feetech registers", formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    # By default we search for all CH430 ports with
    parser.add_argument("--hardware_regex", type=str, default='1A86:7523', help='Serial port filter for detecting multiple boards or specify single board')
    parser.add_argument("--baud", type=int, default=1000000, help='Baudrate')
    parser.add_argument("--protocol", type=int, default=0, help='SCS Protocol')
    parser.add_argument("--id", type=int, help='Servo ID', required=True)
    parser.add_argument("--addr", type=int, help='Register')
    parser.add_argument("--length", type=int, help='Address length in bytes', choices=[1,2])
    parser.add_argument("--negative_bit", type=int, help='Negative sign  bit for this register')
    parser.add_argument("--write", type=int, help='Data to write in the decimal format ')
    parser.add_argument("--action", type=str, help="Defined actions such as set", choices=list(ACTIONS.keys()))
    args = parser.parse_args()
    args = vars(args)
    if args.get('action', False):
        args.update(ACTIONS[args['action']])
    if not args.get('addr', False):
        parser.error("Register address is required")
    if not args.get('length', False):
        parser.error("Register address length is required")
    return args


args = argument_parser()

def find_servo_port(port, baud,  id):
    port = sdk.PortHandler(port)
    handler = sdk.PacketHandler(args['protocol'])
    try:
        port.openPort()
        port.setBaudRate(baud)
        model_number, result, error = handler.ping(port, id)
        if result == sdk.COMM_SUCCESS:
            return port, handler
    except Exception as e:
        print(e)
    return None, None

def find_servo():
    ports = [p.device for p in grep_serial_ports(args['hardware_regex'])]
    for p in ports:
        port, handler =  find_servo_port(p, args['baud'], args['id'])
        if port is not None:
            return port, handler
    print("Servo not found")
    exit(1)

def write(port, handler):
    data = args['write']
    length = args['length']
    # negative values
    if data < 0:
        bit  = args['negative_bit']
        if bit < 2 or bit > length * 8 - 1:
            print("Invalid negative bit")
        data = abs(data) + 2**bit
    if length == 1:
        result, error = handler.write1ByteTxRx(port, args['id'], args['addr'], data)
    if length == 2:
        result, error = handler.write2ByteTxRx(port, args['id'], args['addr'], data)
    if not result == sdk.COMM_SUCCESS:
        print("Error wiriting data")
        exit(1)
    else:
        print("Sucessfully written")
        exit()

def read(port, handler):
    length = args['length']
    if length == 1:
        data, result, error = handler.read1ByteTxRx(port, args['id'], args['addr'])
    if length == 2:
        data, result, error = handler.read2ByteTxRx(port, args['id'], args['addr'])
    if not result == sdk.COMM_SUCCESS:
        print("Error reading data")
        exit(1)
    else:
        if args['negative_bit'] is not None:
            bit = args['negative_bit']
            if data > 2**bit:
                data = 0-data%(2**bit)
        print(data)

def main():
    port, handler = find_servo()
    if args.get('write') is not None:
        write(port, handler)
    else:
        read(port, handler)

if __name__ == '__main__':
    main()