# Overview urt30plus/b3

This is a fork of the Big Brother Bot (B3) that was updated to work with
Python 3 and only supports the Urban Terror 4.3 Game.

<https://github.com/BigBrotherBot/big-brother-bot>

## Requirements

* Python 3.11+

## Running

Use the following command to start the bot

```bash
python3 -m b3 -c ~/.b3/b3.ini
```

## Configuration

Copy the `b3/conf/b3.distribution.ini` file and customize it as needed. The
recommended location for the file is `~/.b3/b3.ini`. By default, the bot will
look for the configuration file in the `~/.b3` directory, in the directory
where `B3` is located or in the `b3/conf` directory.

You can use the `-c` flag to specify the exact path to the configuration file.

## Development on macOS

Clone this repo into `$VIRTUAL_ENV_HOME`.

Setup virtualenv based on Pytohn 3.11: `python3.11 -m venv b3`

Install requirements:

```shell
pip install --upgrade pip
pip install --upgrade --upgrade-strategy eager -r requirements-dev.txt
```
