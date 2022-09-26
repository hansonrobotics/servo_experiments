## REQUIREMENT
 - Python 3.8
 - Serial port access, for Ubuntu current user needs to be in dialout group
 - Feetech SCS or STS servos.
## INSTALLATION
For Ubuntu:

```bash
git clone https://github.com/hansonrobotics/servo_experiments
cd servo_expriments
python3.8 -m venv .venv --python /usr/bin/python3.8
source .venv/bin/activate
pip install -r requirements.txt
```

## Tools

### Ping
Pings all available servos on multiple boards connected
```bash
./ping.py --help
```
```
  -h, --help            show this help message and exit
  --hardware_regex HARDWARE_REGEX
                        Serial port filter for detecting multiple boards (default: 1A86:7523)
  --baud BAUD           Baudrate (default: 1000000)
  --from_id FROM_ID     From ID (default: 0)
  --to_id TO_ID         To ID (default: 110)
  --json JSON           Output as JSON (default: False)
  --find_any FIND_ANY   If True, will print motor ID and return immediatly
                        after found, if none servo found it will fail with
                        exit code 1 (default: False)
```
Examples:
```
 ./ping.py --from_id 80 --to_id 90
```
Output:
```
{'/dev/ttyUSB0': [(83, 6662)]}
```
Where device port is `/dev/ttyUSB0` and `83` is servo ID and `6662` internal servo model.


### RW
Allows to read and write registers to the servo
```bash
./rw.py --help
```

```
usage: rw.py [-h] [--hardware_regex HARDWARE_REGEX] [--baud BAUD]
             [--protocol PROTOCOL] --id ID [--addr ADDR] [--length {1,2}]
             [--negative_bit NEGATIVE_BIT] [--write WRITE]
             [--action {reset_neutral,id}]

Read Write Feetech registers

optional arguments:
  -h, --help            show this help message and exit
  --hardware_regex HARDWARE_REGEX
                        Serial port filter for detecting multiple boards or
                        specify single board (default: 1A86:7523)
  --baud BAUD           Baudrate (default: 1000000)
  --protocol PROTOCOL   SCS Protocol (default: 0)
  --id ID               Servo ID (default: None)
  --addr ADDR           Register (default: None)
  --length {1,2}        Address length in bytes (default: None)
  --negative_bit NEGATIVE_BIT
                        Negative sign bit for this register (default: None)
  --write WRITE         Data to write in the decimal format (default: None)
  --action {reset_neutral,id}
                        Defined actions such as set (default: None)
```
Examples:
Writes goal_position:
```
 ./rw.py --id 3 --addr 42 --length 2 --write 1000
```

Resets servo to neutral:
```
./rw.py --id 3 --action  reset_neutral
```

Reads present position:
```
./rw.py --id 3 --addr 56 --length 2
```


### Meassure
Measures the time it takes for servo to move from one position to another
Usage:
```bash
./meassure.py --help
```
```txt
usage: meassure.py [-h] [--port PORT] [--baud BAUD] [--protocol PROTOCOL] [--id ID] [--from FROM] [--to TO] [--goback GOBACK] [--title TITLE] [--percieved PERCIEVED]

Meassure servo speed based on feedback

optional arguments:
  -h, --help            show this help message and exit
  --port PORT           Serial port (default: /dev/ttyUSB0)
  --baud BAUD           Baudrate (default: 1000000)
  --protocol PROTOCOL   SCS Protocol (default: 0)
  --id ID               Servo ID (default: 1)
  --from FROM           From Position (default: 500)
  --to TO               To Position (default: 1000)
  --goback GOBACK       Meassures time to get back to initial position as well (default: False)
  --title TITLE         Title for graph (default: Servo Position)
  --percieved PERCIEVED
                        Remove first n percent of movement, to show percieved stats (default: 0)
```
Examples:
```bash
./meassure.py --id 1 --protocol 0 --from 300 --to 910 --goback true --percieved 5

```