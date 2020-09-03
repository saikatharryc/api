#!/bin/sh

if [ -z "$*" ]; then echo "No args"; fi
if [[ -f "$1" ]]; then
    echo ""
else
    echo "Please pass JSON"
    exit 0
fi

if [[ $(du $1 | awk '{print $1/1000}') > 1 ]]; then
    echo "Space Limit Exceeded"
    exit 0
fi
DUMP_DATA=curl -X GET \
  $(cat $1 | jq -r '.url') \
  -H 'cache-control: no-cache'

QUERY=$(cat $1 | jq -r '.query' | base64 --decode)


sqlite3 <<EOF
$DUMP_DATA
.timer ON
.header ON
.mode column
.separator ROW "\n"
$QUERY
.quit
EOF
