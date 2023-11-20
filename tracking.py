from math import *
from argparse import *
import configparser
from pdb import set_trace as brk


TYRE_DIAMETER = 492
# How far the tracking gauge sticks out from the edge of the tyre
GAUGE_OFFSET = 86
TYRE_WIDTH = 127


def rad2deg(theta):
	return (theta * 360) / (2*pi)


def deg2rad(theta):
	return (theta * 2*pi) / (360)


def angle_to_mm(angle, tyre_diameter=TYRE_DIAMETER):
	"""Convert a toe in radians to one in mm"""
	return sin(angle) * tyre_diameter


def mm_to_angle(mm, tyre_diameter=TYRE_DIAMETER):
	"""Convert a toe in mm in one in radians"""
	return asin(mm / tyre_diameter)


CORRECT_TOE = mm_to_angle(-1.6)


def calculate_toe(width_a, distance_a, width_b, distance_b):
	"""width_a is the width between the laser dots at distance_a, and width_b
	is the distance between them at distance_b. distance_a should be the
	shorter of the two. Return the total angle in radians, positive for toe in,
	negative for toe out"""
	assert distance_a < distance_b
	adj = distance_b - distance_a
	opp = width_a - width_b
	return atan(opp/adj)


def display_toe(angle):
	"""Display a toe reading in a nice human-readable way given an angle in
	radians"""
	mm = angle_to_mm(angle)
	deg = rad2deg(angle)

	if angle < 0:
		word = "toe-out"
	else:
		word = "toe-in"

	print("Total {} of {:.2f}° or {:.2f}mm".format(word, abs(deg), abs(mm)))


def calculate_track(toe, width, distance):
	"""Given a total toe, a width between dots, and the distance of those dots,
	work out the "track". This is actually the width between where you're
	putting the lasers-- so wider than the actual track measured between tyre
	centres"""
	return width + distance * tan(toe)


def target_width(track, distance, toe=CORRECT_TOE):
	"""How far apart should the dots be for a given toe at a particular
	distance? We need to know the track (not the actual vehicle track-- but how
	far apart the dots would be if the front wheels had zero toe) for
	this"""
	return track - distance * tan(toe)


def main():
	ap = ArgumentParser()
	ap.add_argument("-c", "--config", type=str, default="measurements.ini")

	args = ap.parse_args()
	config = configparser.ConfigParser()
	config.read(args.config)
	brk()

	# It doesn't matter what reference point you use for those distances-- a
	# block of wood in front of the wheel is fine-- but whatever you use you
	# need to use the same one when computing the target width.
	width_a, distance_a = 1351,	1035
	width_b, distance_b = 848, 5230

	toe = calculate_toe(width_a, distance_a, width_b, distance_b)
	display_toe(toe)

	# This should come out exactly the same whichever width/distance you use
	track = calculate_track(toe, width_b, distance_b)

	distances = [distance_a, distance_b]
	targets = [(d, target_width(track, d)) for d in distances]

	for d, w in targets:
		print("Width at {} should be {}".format(d, round(w)))

	while True:
		print("How far is your car away from the wall?")
		inp = input("> ")
		if inp[0] == "q": break

		try: distance = float(inp)
		except ValueError: continue

		print("Width at {} should be {}".format(distance,
			round(target_width(track, distance))))

	print("OK bye")


if __name__ == "__main__":
	main()
