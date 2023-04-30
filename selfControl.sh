#!/usr/bin/bash

LASTTIME=$(date +%s%N)
while true
do
	sleep .1
	CURRTIME=$(date +%s%N)
	echo "Tick: $(( ($CURRTIME - $LASTTIME)/1000000 ))"
	LASTTIME=$CURRTIME
done
