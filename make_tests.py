#!/usr/bin/env python3
# The purpose of this is to simulate the measurements you would get with
# particular error in your tool and given toes to check if tracking.py can
# figure the toes back out again from the data.
import configparser
from tracking import deg2rad, mm_to_angle, CORRECT_TOE
from math import *
from pdb import set_trace as brk


def add_error(config, fname, error_toe):
	actual_front_toe = CORRECT_TOE.front
	actual_rear_toe = CORRECT_TOE.rear
	track = 1511.3, 1483.79

	with open(fname, "w") as fp:
		for section_name in config.sections():
			print("[{}]".format(section_name), file=fp)
			section = config[section_name]
			print("distance = {}".format(section["distance"]), file=fp)
			distance = float(section["distance"])

			if "Forwards" in section_name: s = 1
			else: s = -1

			front = track[0] - tan(s * actual_front_toe + error_toe) * distance
			rear = track[1] - tan(s * actual_rear_toe + error_toe) * distance

			print("front = {}".format(front), file=fp)
			print("rear = {}\n".format(rear), file=fp)

	print("Wrote", fname)


def main():
	config = configparser.ConfigParser()
	config.read("measurements.ini")

	# Simulate measurements with a tool that systematically toes in
	add_error(config, "toed_in.ini", deg2rad(0.0))

	# Simulate measurements with a tool that systematically toes out
	add_error(config, "toed_out.ini", -0.0027)


if __name__ == "__main__":
	main()
