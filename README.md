boblib
=
Please see the Wiki-Page for a documentation of public methods and their attributes.

# Short description of how to use it
This is a short HowTo you need to get it running.

* import the library: `import boblib`
* instantiate: `bob = boblib.Boblight("127.0.0.1", 19333)`
* set colors of all lights (i.e.: yellow): `bob.setColor(1, 1, 0)`
* set priority: `bob.setPriority(128)`
* set speed of all lights: `bob.setSpeed(0.5)`
* set interpolation of all lights: `bob.setInterpolation(True)`
* set color of a specific light (i.e.: 12 to red): `bob.getLight()[13].getColor().setColor(1, 0, 0)`
* set speed of a specific light (i.e.: 12): `bob.getLight()[13].setSpeed(1)`
* set interpolation of a specific light (i.e.: 12): `bob.getLight()[13].setInterpolation(False)`
* disconnect from server: `bob.disconnect()`

In one of my projects I needed to store information about "who" set a light. Let's say the user sets a few lights to specific colors and the software calculates the colors of all other lights to get a color gradient.

* set setManually of a specific light (i.e.: 12): `bob.getLight()[13].setSetManually(True)`
