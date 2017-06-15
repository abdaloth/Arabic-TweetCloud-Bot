#!/bin/sh
# botlauncher.sh
# navigate home then to this dir then runs this bot

cd /
cd home/pi/TwitterBot
sudo python3 tootbot.py > logs/botlog
cd /


