from math import *

FRONT_TRACK = 1240
REAR_TRACK = 1210

# How far the tracking gauge sticks out from the edge of the tyre
GAUGE_OFFSET = 86

RIM_WIDTH = 127


def rear_toe(w, a, b):
	"""a and b are the distances along the lasers measured backwards to the
	garage door. w is the width between where they join"""
	# This is the width you would expect between the two dots if the rear
	# wheels were parallel, i.e. not toed at all.
	p = REAR_TRACK + GAUGE_OFFSET * 2 + RIM_WIDTH

	# p is bigger than w. This isn't right. The rear wheels are supposed to toe
	# in so w ought to be greater (and by more the further you drive away from
	# the door).
	print(p, w, p-w)


def rad2deg(theta):
	return (theta * 360) / (2*pi)


def deg2rad(theta):
	return (theta * 2*pi) / (360)


def angle(w1, w0, a, b, c, d):
	"""w1 and w0 are the two widths projected out by the lasers on the garage
	door. a, b, c, and d are the lengths from each wheel to the dots on the
	door"""
	total = sum((a, b, c, d))
	return asin((w1 - w0) / total)


# theta = angle(1490, 1369, 2684, 2646, 2487 + 2036, 2420 + 2036)
# print(theta, rad2deg(theta))

rear_toe(1490, 2684, 2646)
