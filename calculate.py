from math import *


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


theta = angle(1490, 1369, 2684, 2646, 2487 + 2036, 2420 + 2036)
print(theta, rad2deg(theta))
