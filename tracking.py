#!/usr/bin/env python3
from math import *
from argparse import *
import configparser
from collections import namedtuple
from pdb import set_trace as brk


TYRE_DIAMETER = 473
# How far the tracking gauge sticks out from the edge of the tyre
WHEELBASE = 2040


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


CorrectToe = namedtuple("CorrectToe", "front rear")
CORRECT_TOE = CorrectToe(mm_to_angle(-1.6),
		mm_to_angle(3.17))


def calculate_toe(width_a, distance_a, width_b, distance_b):
	"""width_a is the width between the laser dots at distance_a, and width_b
	is the distance between them at distance_b. distance_a should be the
	shorter of the two. Return the total angle in radians, positive for toe in,
	negative for toe out"""
	assert distance_a < distance_b
	adj = distance_b - distance_a
	opp = width_a - width_b
	return atan(opp/adj)


def display_toe(angle, caption=""):
	"""Display a toe reading in a nice human-readable way given an angle in
	radians"""
	mm = angle_to_mm(angle)
	deg = rad2deg(angle)

	if angle < 0:
		word = "toe-out"
	else:
		word = "toe-in"

	print("{}Total {} of {:.2f}° or {:.2f}mm".format(
		caption, word, abs(deg), abs(mm)))


def calculate_track(toe, width, distance):
	"""Given a total toe, a width between dots, and the distance of those dots,
	work out the "track". This is actually the width between where you're
	putting the lasers-- so wider than the actual track measured between tyre
	centres"""
	return width + distance * tan(toe)


def target_width(track, distance, toe=CORRECT_TOE.front):
	"""How far apart should the dots be for a given toe at a particular
	distance? We need to know the track (not the actual vehicle track-- but how
	far apart the dots would be if the front wheels had zero toe) for
	this"""
	return track - distance * tan(toe)


class Measurement:
	def __init__(self):
		"""Note these are proper distances, with wheelbases added where
		necessary, not the "raw" distances recorded in the config file"""
		self.distance = None
		self.width = None

	def __repr__(self):
		return "{} {}".format(self.distance, self.width)


class Calculation:
	def __init__(self, measurement_a, measurement_b):
		self.measurement_a = measurement_a
		self.measurement_b = measurement_b
		self.toe = self.calculate_toe()

	def calculate_toe(self):
		return calculate_toe(self.measurement_a.width,
				self.measurement_a.distance,
				self.measurement_b.width,
				self.measurement_b.distance)


class MeasurementSet:
	"""One of these for each axle"""
	def __init__(self):
		self.forwards_near = Measurement()
		self.forwards_far = Measurement()
		self.backwards_near = Measurement()
		self.backwards_far = Measurement()

	def estimate_error(self):
		"""The toes measured forwards and backwards should sum to zero.
		Whatever they sum to, divided by two, is the error in your measurement
		device, which we hope is consistent"""
		forwards = Calculation(self.forwards_near, self.forwards_far)
		backwards = Calculation(self.backwards_near, self.backwards_far)

		return (forwards.toe + backwards.toe) / 2

	def calculate_toe(self, error):
		calc = Calculation(self.forwards_near, self.forwards_far)
		return calc.toe - error

	def __repr__(self):
		return """
Forwards Near: {}
Forwards Far: {}
Backwards Near: {}
Backwards Far: {}""".format(self.forwards_near,
		self.forwards_far,
		self.backwards_near,
		self.backwards_far)


def parse_config(config):
	"""Returns two MeasurementSets for the front and rear axles respectively"""
	front, rear = MeasurementSet(), MeasurementSet()

	for their_name, our_name in (
			("Forwards Near", "forwards_near"),
			("Forwards Far", "forwards_far"),
			("Backwards Near", "backwards_near"),
			("Backwards Far", "backwards_far")):
		conf = config[their_name]
		distance = float(conf["distance"])

		front_measurement = getattr(front, our_name)
		front_measurement.distance = distance
		front_measurement.width = float(conf["front"])

		rear_measurement = getattr(rear, our_name)
		rear_measurement.distance = distance
		rear_measurement.width = float(conf["rear"])

		if "Forwards" in their_name:
			rear_measurement.distance += WHEELBASE
		else:
			front_measurement.distance += WHEELBASE

	return front, rear


Targets = namedtuple("Targets", "distance front_forwards front_backwards"
		" rear_forwards rear_backwards")


def calculate_targets(d, error, front_track, rear_track):
	ret = [d]
	for axle, track, toe in (("front", front_track, CORRECT_TOE.front),
			("rear", rear_track, CORRECT_TOE.rear)):
		for direction, sign in (
				("forwards", 1),
				("backwards", -1)):
			ret.append(target_width(track, d, toe * sign + error))
	return Targets(*ret)


def display_targets(targets):
	print("Targets:")
	for t in targets:
		for axle in ("front", "rear"):
			for direction in ("forwards", "backwards"):
				width = getattr(t, "{}_{}".format(axle, direction))
				print("Width projected from {} wheels, car facing {}, "
						"at {}: {}".format(axle, direction,
							round(t.distance),
							round(width)))


def main():
	ap = ArgumentParser()
	ap.add_argument("-c", "--config", type=str, default="measurements.ini")
	ap.add_argument("-i", "--interactive", action="store_true")

	args = ap.parse_args()
	config = configparser.ConfigParser()
	config.read(args.config)

	front, rear = parse_config(config)
	errors = [front.estimate_error(), rear.estimate_error()]
	print("Error of the tool, front and rear estimates: {:.2f}° {:.2f}°"
			.format(rad2deg(errors[0]), rad2deg(errors[1])))

	# We use the error measured at the rear axle on the basis that since there
	# is no steering there it's possible it's slightly more reliable.
	error = errors[1]

	print("Using an error of {:.4f} radians ({:.2f}°)\n".
			format(error, rad2deg(error)))

	# OK so now calculate the actual front and rear toe
	front_toe = front.calculate_toe(error)
	display_toe(front_toe, "Front ")

	rear_toe = rear.calculate_toe(error)
	display_toe(rear_toe, "Rear ")

	front_track = calculate_track(front_toe + error, front.forwards_far.width,
			front.forwards_far.distance)
	print("Front track (between where the laser was) is"
			" {:.2f}mm".format(front_track))

	rear_track = calculate_track(rear_toe + error, rear.forwards_far.width,
			rear.forwards_far.distance)
	print("Rear track (between where the laser was) is"
			" {:.2f}mm\n".format(rear_track))

	# Now work out targets for correctly setting the front and rear toes.
	distances = [front.forwards_near.distance, front.forwards_far.distance]
	targets = [calculate_targets(d, error, front_track, rear_track)
			for d in distances]
	display_targets(targets)

	if not args.interactive:
		return

	while True:
		print("\nHow far is your car away from the wall?")
		inp = input("> ")
		if not inp or inp[0] == "q": break

		try: distance = float(inp)
		except ValueError: continue

		display_targets([calculate_targets(distance,
			error, front_track, rear_track)])

	print("OK bye")


if __name__ == "__main__":
	main()
