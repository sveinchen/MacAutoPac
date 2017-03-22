#!/bin/sh

AUTOPAC_URL="https://raw.githubusercontent.com/sveinchen/MacAutoPac/master/bin/autopac.py"
PLIST_URL="https://raw.githubusercontent.com/sveinchen/MacAutoPac/master/io.github.sveinchen.autopac.plist"

BIN_PATH="/usr/local/bin/autopac"
PLIST_PATH="/Library/LaunchDaemons/${PLIST_URL##*/}"

INI_PATH="/usr/local/etc/autopac.ini"
read -r -d '' INI_TMPL <<- EOF
[AutopacDefaults]
;; pac_url = http://example.com/path/to/proxy.pac
;; static_addr = 127.0.0.1

[WiFI-SSID]
;; pac_url = http://another.com/path/to/proxy.pac
;; static_addr = 10.0.0.1
EOF

curl -fsSL $AUTOPAC_URL > $BIN_PATH

chmod +x $BIN_PATH

if [ -e "$PLIST_PATH" ]; then
    cd ${PLIST_PATH%/*} && sudo launchctl unload -w ${PLIST_URL##*/}
fi

sudo touch $PLIST_PATH
curl -fsSL $PLIST_URL  | sudo tee $PLIST_PATH > /dev/null

cd ${PLIST_PATH%/*} && sudo launchctl load -w ${PLIST_URL##*/}

touch $INI_PATH
echo "$INI_TMPL" > $INI_PATH

echo ">>> Edit config file at: \"$INI_PATH\"" 
echo ">>> enjoy!"
