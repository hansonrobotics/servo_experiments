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

from ast import Return
from dataclasses import dataclass
import time
import argparse
import time
import scservo_sdk as sdk
import matplotlib.pyplot as plt
import numpy as np

# Control table address
ADDR_SCS_TORQUE_ENABLE     = 40
ADDR_SCS_GOAL_ACC          = 41
ADDR_SCS_GOAL_POSITION     = 42
ADDR_SCS_GOAL_SPEED        = 46
ADDR_SCS_PRESENT_POSITION  = 56
MOVING_THRESHOLD = 5
STEPS_IN_DEG = {
    0: 11.38,
    1: 4.65,
}

def argument_parser():
    parser = argparse.ArgumentParser(description="Meassure servo speed based on feedback", formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument("--port", type=str, default='/dev/ttyUSB0', help='Serial port')
    parser.add_argument("--baud", type=int, default=1000000, help='Baudrate')
    parser.add_argument("--protocol", type=int, default=0, help='SCS Protocol')
    parser.add_argument("--id", type=int, default=1, help='Servo ID')
    parser.add_argument("--from", type=int, default=500, help='From Position')
    parser.add_argument("--to", type=int, default=1000, help='To Position')
    parser.add_argument("--goback", type=bool, default=False, help='Meassures time to get back to initial position as well')
    parser.add_argument("--title", type=str, default="Servo Position", help='Title for graph')
    parser.add_argument("--percieved", type=int, default=0, help='Remove first n percent of movement, to show percieved stats')

    args = parser.parse_args()
    return vars(args)



def plot(x, y, xlabel='Time (s)', ylabel='Degrees', title='Servo Position'):
    plt.plot(x, y)
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    plt.title(title)
    plt.show()


def move_to(group_sync_write, id, position):
    param_goal_position = [sdk.SCS_LOBYTE(position), sdk.SCS_HIBYTE(position)]
    group_sync_write.addParam(id, param_goal_position)
    group_sync_write.txPacket()
    group_sync_write.clearParam()

def move_to_single(port, packets, id, position):
    packets.write2ByteTxRx(port, id, ADDR_SCS_GOAL_POSITION, position)

def current_position(group_sync_read, id, ph=None):
    scs_comm_result = group_sync_read.txRxPacket()
    if scs_comm_result != 0:
        print("Error")
        print(ph.getTxRxResult(scs_comm_result))

    data = group_sync_read.getData(id, ADDR_SCS_PRESENT_POSITION, 2)
    return data

def current_position_single(port, packets, id):
    data, status, error = packets.read2ByteTxRx(port, id, ADDR_SCS_PRESENT_POSITION)
    if status or error:
        raise Exception(f"Error reading position: {status} {error}")
    return data




def main():
    args = argument_parser()
    port = sdk.PortHandler(args['port'])
    print(args['protocol'])

    packets = sdk.PacketHandler(args['protocol'])
    if not port.openPort() and port.setBaudRate(args['baud']):
        print(f"Cant Open port {args['port']}")
        return
    id = args['id']
    scs_model_number, scs_comm_result, scs_error = packets.ping(port, id)
    if scs_comm_result or scs_error:
        print("Cant ping servo")
        return
    else:
        print(f"Servo with ID: {id} is found. Model {scs_model_number}")
    times, positions = meassure(port, packets, id, args['from'], args['to'], args['goback'], STEPS_IN_DEG[args['protocol']])
    if args['percieved'] > 0:
        percieved_angle_threshold = (args['to'] - args['from']) * args['percieved'] / 100 / STEPS_IN_DEG[args['protocol']]
        print(percieved_angle_threshold)
        times, positions = perceived_data(times, positions, percieved_angle_threshold)
        print(f'Starting: {times[0]}, duration: {times[-1] - times[0]}')

    plot(times, positions, args['title'])

def perceived_data(times, positions,threshold):
    percieved_times = []
    percieved_positions = []
    for p,t in zip(positions, times):
        if abs(p) > abs(threshold):
            percieved_positions.append(p)
            percieved_times.append(t)
    return percieved_times, percieved_positions

def meassure(port,packets, id, start, end, back=True, steps_in_deg=1):
    group_sync_read = sdk.GroupSyncRead(port, packets, ADDR_SCS_PRESENT_POSITION, 2)
    group_sync_read.addParam(id)
    group_sync_write = sdk.GroupSyncWrite(port, packets, ADDR_SCS_GOAL_POSITION, 2)
    move_to(group_sync_write, id, start)
    print("Moving to initial position")
    time.sleep(1)
    #starting = current_position(group_sync_read, id, packets)
    starting = current_position_single(port, packets, id)
    time.sleep(1)
    print(f"Starting position: {starting}")
    # position
    positions = [starting]
    start_time = time.perf_counter()
    times = [0]
    current = starting
    move_to(group_sync_write, id, end)
    #move_to_single(port, packets, id, end)
    goal = end
    while True:
        current = current_position_single(port, packets, id)
        positions.append(current)
        times.append(time.perf_counter() - start_time)
        if abs(goal-current) < MOVING_THRESHOLD + 50*back:
            if back:
                back = False
                goal = start
                move_to(group_sync_write, id, goal)
            else:
                break
    if back:
       move_to(group_sync_write, id, start)
    print(f"Movement finished in {times[-1]} seconds. samples {len(times)}")
    positions = [(p-start)/steps_in_deg for p in positions]
    return times, positions

if __name__ == '__main__':
    main()
