from math import *
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


def main():
	width_a, distance_a = 1351,	1035
	width_b, distance_b = 848, 5230
	toe = calculate_toe(width_a, distance_a, width_b, distance_b)
	display_toe(toe)

	print(calculate_track(toe, width_a, distance_a))
	print(calculate_track(toe, width_b, distance_b))

	# Given the track and the desired angle it should be fairly easy to work
	# out the measurements you should be shooting for at those two distances.
	# TODO YOU ARE HERE.


if __name__ == "__main__":
	main()