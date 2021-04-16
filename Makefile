export:
	mkdir -p bin
	blender -b test_scenes/Cube.blend --python export.py -- --output-file="bin/Cube.scn"
	blender -b test_scenes/PhysicsTest.blend --python export.py -- --output-file="bin/PhysicsTest.scn"
