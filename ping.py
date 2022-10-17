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
from sys import exit
import argparse
import json
from pprint import pprint as pp
from serial.tools.list_ports import grep as grep_serial_ports
import scservo_sdk as sdk


def argument_parser():
    parser = argparse.ArgumentParser(description="Ping all feetech servos", formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    # By default we search for all CH430 ports with
    parser.add_argument("--hardware_regex", type=str, default='1A86:7523', help='Serial port filter for detecting multiple boards or specify single board')
    parser.add_argument("--baud", type=int, default=1000000, help='Baudrate')
    parser.add_argument("--from_id", type=int, default=0, help='From ID')
    parser.add_argument("--to_id", type=int, default=110, help='To ID')
    parser.add_argument("--json", type=bool, default=False, help="Output as JSON")
    parser.add_argument("--find_any", type=bool, default=False, help="If True, will print motor ID and return immediatly after found, if none servo found it will fail with exit code 1")
    args = parser.parse_args()
    return vars(args)
# Global dictionary for args
args = argument_parser()

def pingservos(port, baud, from_id, to_id):
    port = sdk.PortHandler(port)
    # Ping does not depend on the protocol version so can use 0 by default
    handler = sdk.PacketHandler(0)
    servos = []
    try:
        port.openPort()
        port.setBaudRate(baud)
        for id in range(from_id, to_id+1):
            # Ping the servo
            model_number, result, error = handler.ping(port, id)
            if result == sdk.COMM_SUCCESS:
                servos.append((id, model_number))
                if args['find_any']:
                    servo_found(id)
        return servos
    except Exception as e:
        print(e)
        return None

def find_all_servos():
    ports = [p.device for p in grep_serial_ports(args['hardware_regex'])]
    devices = {}
    for p in ports:
        devices[p] = pingservos(p, args['baud'], args['from_id'], args['to_id'])
    return devices

def servo_found(id):
    # Simple output
    print(id)
    exit(0)

def main():
    device_servos = find_all_servos()
    if args['find_any']:
        print("No servo found")
        exit(1)

    if args['json']:
        print(json.dumps(device_servos, indent=4, sort_keys=True))
    else:
        pp(device_servos)

if __name__ == '__main__':
    main()
