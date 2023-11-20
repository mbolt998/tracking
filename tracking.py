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


def target_width(track, distance, toe=CORRECT_TOE):
	"""How far apart should the dots be for a given toe at a particular
	distance? We need to know the track (not the actual vehicle track-- but how
	far apart the dots would be if the front wheels had zero toe) for
	this"""
	return track - distance * tan(toe)


class Measurement:
	def __init__(self):
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
		return calc.toe + error

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

	return front, rear


def main():
	ap = ArgumentParser()
	ap.add_argument("-c", "--config", type=str, default="measurements.ini")

	args = ap.parse_args()
	config = configparser.ConfigParser()
	config.read(args.config)

	front, rear = parse_config(config)
	errors = [front.estimate_error(), rear.estimate_error()]
	print("Error of the tool based on the front and rear axles: {:.2f}° {:.2f}°"
			.format(rad2deg(errors[0]), rad2deg(errors[1])))

	# We'll use the average error
	error = sum(errors) / 2

	print("Using an average error of {:.4f} radians ({:.2f}°)".
			format(error, rad2deg(error)))

	# OK so now calculate the actual front and rear toe
	front_toe = front.calculate_toe(error)
	display_toe(front_toe, "Front ")

	rear_toe = rear.calculate_toe(error)
	display_toe(rear_toe, "Rear ")

	track = calculate_track(front_toe, front.forwards_far.width,
			front.forwards_far.distance)
	print("Track (between where the laser was) is {:.2f}mm".format(track))

	# Now work out targets for correctly setting the front toe. The rear isn't
	# adjustable.
	distances = [front.forwards_near.distance, front.forwards_far.distance]

	def target(d):
		return target_width(track, d, CORRECT_TOE + error)

	targets = [(d, target(track)) for d in distances]

	for d, w in targets:
		print("Width at {} should be {}".format(d, round(w)))

	while True:
		print("How far is your car away from the wall?")
		inp = input("> ")
		if inp[0] == "q": break

		try: distance = float(inp)
		except ValueError: continue

		print("Width at {} should be {}".format(distance, round(target(track))))

	print("OK bye")


if __name__ == "__main__":
	main()
