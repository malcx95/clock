# Clock - track your working hours

This is a simple command line tool to track your working hours. You can see per month how much you have deviated from 8 hours/day.


## Installation

Just download this script and run it. To make it accessible everywhere, you can add it to your PATH or move it to `/usr/local/bin`:

```bash
sudo cp clock.py /usr/local/bin/clock
```

## Usage

To start a working day, run

```bash
clock -i
```

To start lunch, run

```bash
clock -l
```

To end lunch, run

```bash
clock -e
```

To end the working day, run

```bash
clock -o
```

If you need to take a non-lunch break for which you don't want to count as working time (pause), you can use the `-p` option:

```bash
clock -p
```

To end a pause, run

```bash
clock -t
```

At any time, you can view this day's status by running

```bash
clock -s
```

To see this month's summary, run

```bash
clock -m
```
