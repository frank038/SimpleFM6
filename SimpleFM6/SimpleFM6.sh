#!/bin/bash
thisdir=$(dirname "$0")
cd $thisdir
# chromium hack
DOWNLOAD="$HOME/Downloads/"
if [[ "$@" = "." && -d "$DOWNLOAD" ]]; then
  NEWFILE=`ls -Art $DOWNLOAD | tail -n 1`
  python3 SimpleFM6.py "$DOWNLOAD/$NEWFILE" &
else
  python3 SimpleFM6.py "$@" &
fi

cd $HOME
