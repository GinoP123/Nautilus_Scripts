#!/usr/bin/env python3

import sys


config = {
	'port': '8888',
	'pvc_profiles': {
		'bafnavol': '/home/bafnavol/giprasad/.profile',
		'ecvol': '/home/ecvol/.profile'
	},
}


if __name__ == "__main__":
	print(config[sys.argv[1]])
