#!/usr/bin/env python

glo_bobcat_url = "http://bobcatminer.fritz.box"
glo_fritzbox_url = "http://fritz.box"
glo_fritzbox_user = "<FRITZ!Box user name>"
glo_fritzbox_pass = "<FRITZ!Box password>"
glo_outlet_ain = "<AIN of the power outlet>"
glo_retry_count = 5
glo_retry_sleep = 30 # seconds
glo_restart_sleep = 30 # seconds

import argparse
import hashlib
import logging
import urllib2
import re
import sys
import time

def get(addr):
	logging.info("GET: " + addr)
	return urllib2.urlopen(addr).read()

def bobcat_is_fine():
	for _ in range(glo_retry_count):
		try:
			json = get(glo_bobcat_url + "/status.json")
			return True, json
		except:
			pass
		time.sleep(glo_retry_sleep)
	return False, ""

def fritzbox_login():
	html = get(glo_fritzbox_url + "/login_sid.lua")
	logging.debug("HTML: " + html)
	challenge = re.search(r'<Challenge>(.+?)</Challenge>', html).group(1)
	logging.debug("Challenge: " + challenge)
	challengestr = challenge + "-" + glo_fritzbox_pass
	response = hashlib.md5(challengestr.encode('utf-16le')).hexdigest()
	logging.debug("Response: " + response)
	html = get(glo_fritzbox_url + "/login_sid.lua?username=" + glo_fritzbox_user + "&response=" + challenge + "-" + response)
	logging.debug("HTML: " + html)
	session_id = re.search(r'<SID>(.+?)</SID>', html).group(1)
	logging.debug("SID: " + session_id)
	return session_id

def fritzbox_logout(session_id):
	html = get(glo_fritzbox_url + "/login_sid.lua?logout=yes&sid=" + session_id)
	logging.debug("HTML: " + html)

def restart_fritzbox_outlet():
	logging.info("FRITZ!Box Login")
	session_id = fritzbox_login()
	logging.info("Switching off power outlet")
	html = get(glo_fritzbox_url + "/webservices/homeautoswitch.lua?ain=" + glo_outlet_ain + "&switchcmd=setswitchoff&sid=" + session_id)
	logging.info("Sleeping " + str(glo_restart_sleep) + " seconds")
	time.sleep(glo_restart_sleep)
	logging.info("Switching on power outlet")
	html = get(glo_fritzbox_url + "/webservices/homeautoswitch.lua?ain=" + glo_outlet_ain + "&switchcmd=setswitchon&sid=" + session_id)
	logging.info("FRITZ!Box Logout")
	fritzbox_logout(session_id)

def main():
	parser = argparse.ArgumentParser()
	parser.add_argument(
		"-log",
		"--log",
		default="warning",
		help=("Provide log level. Example --log debug', default='warning'"),
	)
	args = parser.parse_args()
	logging.basicConfig(level=args.log.upper())
	logging.info("Let's go")
	count = 0
	while True:
		count+=1
		ok, json = bobcat_is_fine()
		if ok:
			break

		logging.warning("Bobcat seems to be down!")
		if count > glo_retry_count:
			logging.error("Could not fix bobcat! Please check manually.")
			sys.exit(1)
		else:
			logging.warning("Attempting a restart")
			restart_fritzbox_outlet()
			continue

	logging.info("Bobcat is up")
	logging.info(json)
	logging.info("Bye")

if __name__ == "__main__":
	main()

# EOF
