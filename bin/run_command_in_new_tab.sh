#!/bin/bash

cmd="$@"
if [[ $(uname -s) == 'Darwin' ]]; then
	ttab $cmd
else
	gnome-terminal --tab --title="nautilus" -- /bin/bash -c "$cmd" 2> /dev/null & disown
fi

