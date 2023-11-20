This is a program for checking and setting your front wheel alignment with a
laser pointer and a computer.

First you will need to make some kind of a jig for your laser pointer to hold
it parallel to a wheel in a consistent way.

First check the alignment of the laser pointer itself: mine was terrible. So I
ended up mounting the laser pointer itself at an angle inside a larger diameter
piece of steel tube, so that the laser was parallel to the tube. The best way
to check the alignment is to hold the laser against a flat surface and see
where the dot is at a distance of a couple of metres and whether it moves as
you rotate the laser. This will give pretty high accuracy.

Once you have your laser all jigged up the basic procedure is going to consist
of parking the car in front of a flat object like a garage door, projecting
dots from each wheel on an axle onto the door, and measuring the distance
between those dots.

So you project a dot from the left wheel, and mark where it hits with a sharpie
(I stick a bit of masking tape onto the door first, which I can then write on
with the sharpie). Then move the laser from the left wheel to the right wheel,
and get another dot. The distance between those dots is your measurement.

You will be doing four sets of measurements in total, from two distances (1m
and 5m is good, but you can use whatever you like-- the longer the distances
the more accurate the measurement will be), in both directions.

Then you need to record those results into a ".ini" file. measurements.ini is
an example.

This is divided into four sections, for each set of measurements. "[Forwards
Near]" for example, contains the measurements for when the car is facing
towards the door, at the shorter of your two distances.

It doesn't really matter how you measure the distance from the door to the car,
so long as you are consistent. I measured 1m with a tape measure and put some
blocks of wood on the ground at that point. Then I could drive the car up until
the tyres just touched the blocks.

Within each section there are three measurements, all in millimetres:

distance: the distance of the axle to the door

front: the spacing between the two dots projected onto the door from the two
wheels on the front axle.

rear: the spacing between the two dots projected onto the door from the two
wheels on the rear axle.

Now the code itself (tracking.py) contains two constants, near the top,
TYRE_DIAMETER and WHEELBASE, both in mm, which are set up for a classic Mini
with 10" wheels.

If you have a different vehicle you will need to change these.

It contains another constant, a little further down, called CORRECT_TOE, which
contains the target numbers for a classic Mini. You would need to change those
as well for a different vehicle.

Then when you're all set run:

$ python3 tracking.py -c my_measurements.ini

(assuming you put your measurements in a file called my_measurements.ini)

The software will use the differences between measurements facing forwards and
backwards to cancel out any systemic inaccuracies in your laser jig. So you
should be OK if you're consistent.

It should spit out some output like this:

	Error of the tool, front and rear estimates: -0.38° -0.15°
	Using an error of -0.0027 radians (-0.15°)

	Front Total toe-in of 3.28° or 27.08mm
	Rear Total toe-in of 0.98° or 8.05mm
	Front track (between where the laser was) is 1511.30mm
	Rear track (between where the laser was) is 1513.08mm

	Targets:
	Width projected from front wheels, car facing forwards, at 1030: 1518
	Width projected from front wheels, car facing backwards, at 1030: 1511
	Width projected from rear wheels, car facing forwards, at 1030: 1509
	Width projected from rear wheels, car facing backwards, at 1030: 1523
	Width projected from front wheels, car facing forwards, at 5000: 1542
	Width projected from front wheels, car facing backwards, at 5000: 1508
	Width projected from rear wheels, car facing forwards, at 5000: 1493
	Width projected from rear wheels, car facing backwards, at 5000: 1560

As you can see in this example this particular car is quite far from correct.
The "Targets" are what those widths should be. So with your car parked in the
right place, you can just adjust the track rod ends until the dots are the
correct distance apart. I did this at 5m facing forwards.

Does it work?

I've validated the software (make_tests.py) and set my own car up
with this. It drives fine but then it would. I won't know for some time if I am
getting uneven tyre wear. Good luck!
