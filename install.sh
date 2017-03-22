#!/bin/sh

AUTOPAC_URL="https://raw.githubusercontent.com/sveinchen/MacAutoPac/master/bin/autopac.py"
PLIST_URL="https://raw.githubusercontent.com/sveinchen/MacAutoPac/master/io.github.sveinchen.autopac.plist"

BIN_PATH="/usr/local/bin/autopac"
PLIST_PATH="/Library/LaunchDaemons/${PLIST_URL##*/}"

if [ ! -e "$BIN_PATH" ]; then
    curl -fsSL $AUTOPAC_URL > $BIN_PATH
fi

chmod +x $BIN_PATH

if [ ! -e "$PLIST_PATH" ]; then
    sudo touch $PLIST_PATH
    curl -fsSL $PLIST_URL  | sudo tee $PLIST_PATH > /dev/null
fi

cd ${PLIST_PATH%/*} && sudo launchctl load -w ${PLIST_URL##*/}

echo ">>> enjoy!"
