#!/usr/bin/env python3

import sys


config = {
	'port': '8888',
	'pvc_list': ['bafnavol', 'ecvol'],
	'username': 'giprasad',
}


if __name__ == "__main__":
	assert sys.argv[1] in config
	print(config[sys.argv[1]])
