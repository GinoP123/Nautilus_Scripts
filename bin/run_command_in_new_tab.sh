#!/bin/bash

if [[ $(uname -s) == 'Darwin' ]]; then
	ttab $@
else
	gnome-terminal -- bash -c "$@"
fi

