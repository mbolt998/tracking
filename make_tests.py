import configparser
from tracking import deg2rad, mm_to_angle, CORRECT_TOE
from math import *
from pdb import set_trace as brk


# Create some deliberately inaccurate measurements to check our calculations

def add_error(config, fname, toe):
	actual_front_toe = CORRECT_TOE
	actual_rear_toe = mm_to_angle(3.0)
	track = 1478.41

	t = tan(toe)
	with open(fname, "w") as fp:
		for section_name in config.sections():
			print("[{}]".format(section_name), file=fp)
			section = config[section_name]
			print("distance = {}".format(section["distance"]), file=fp)
			distance = float(section["distance"])

			front = track - tan(actual_front_toe) * distance
			rear = track - tan(actual_rear_toe) * distance

			print("front = {}".format(front), file=fp)
			print("rear = {}\n".format(rear), file=fp)

	print("Wrote", fname)


def main():
	config = configparser.ConfigParser()
	config.read("measurements.ini")

	# Simulate measurements with a tool that systematically toes in
	add_error(config, "toed_in.ini", deg2rad(0))

	# Simulate measurements with a tool that systematically toes out
	add_error(config, "toed_out.ini", deg2rad(-0.5))


if __name__ == "__main__":
	main()
