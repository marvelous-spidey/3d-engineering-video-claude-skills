#!/bin/bash
# usage: bash up.sh <file> <content-type> <presigned url>
code=$(curl -s -o /tmp/put.out -w '%{http_code}' -X PUT -H "Content-Type: $2" -H "If-None-Match: *" --data-binary @"$1" "$3"); echo "PUT $1 $code"; [ "$code" = 200 ] || head -c 300 /tmp/put.out
