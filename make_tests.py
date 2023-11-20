import configparser
from tracking import deg2rad
from math import *
from pdb import set_trace as brk


# Create some deliberately inaccurate measurements from measurements.ini to
# check our results

def add_error(config, fname, toe):
	at = atan(toe)
	with open(fname, "w") as fp:
		for section_name in config.sections():
			print("[{}]".format(section_name), file=fp)
			section = config[section_name]
			print("distance = {}".format(section["distance"]), file=fp)
			distance = float(section["distance"])

			front = float(section["front"]) - at * distance
			rear = float(section["rear"]) - at * distance

			print("front = {}".format(front), file=fp)
			print("rear = {}\n".format(rear), file=fp)

	print("Wrote", fname)


def main():
	config = configparser.ConfigParser()
	config.read("measurements.ini")

	# Simulate measurements with a tool that systematically toes in
	add_error(config, "toed_in.ini", deg2rad(0.5))

	# Simulate measurements with a tool that systematically toes out
	add_error(config, "toed_out.ini", deg2rad(-0.5))


if __name__ == "__main__":
	main()
