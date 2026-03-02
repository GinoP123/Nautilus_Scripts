#!/bin/bash

wake_time="19:00"
curr_time=$(date +\%s)
scheduled_wake_today=$(date +\%s -d "today $wake_time")
scheduled_wake_tomorrow=$(date +\%s -d "tomorrow $wake_time")

if (( $scheduled_wake_today > $curr_time )); then
	next_scheduled_wake=$scheduled_wake_today
else
	next_scheduled_wake=$scheduled_wake_tomorrow
fi

/usr/sbin/rtcwake -m no -t $next_scheduled_wake
