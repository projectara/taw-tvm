#!/bin/sh
/usr/bin/xmonad &
exec /usr/bin/xterm -e sudo ./taw.py
