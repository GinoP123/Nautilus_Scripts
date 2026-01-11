#!/bin/bash

curr_time=$(date +\%s)
scheduled_wake_today=$(date +\%s -d "today 19:00")
scheduled_wake_tomorrow=$(date +\%s -d "tomorrow 19:00")

if (( $scheduled_wake_today > $curr_time )); then
	next_scheduled_wake=$scheduled_wake_today
else
	next_scheduled_wake=$scheduled_wake_tomorrow
fi

/usr/sbin/rtcwake -m no -t $next_scheduled_wake
