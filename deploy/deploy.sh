#!/bin/bash

set -e

CGO_ENABLED=0 GOOS=linux GOARCH=arm go build
ssh rpi systemctl stop bot
scp messiah_bot rpi:/opt/bot/
ssh rpi systemctl start bot
