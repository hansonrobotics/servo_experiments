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