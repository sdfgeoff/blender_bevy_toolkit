
.PHONY: assets

assets:
	rm -r assets || true
	blender -b test_scenes/Cube.blend --python export.py -- --output-file="assets/scenes/Cube.scn"
	blender -b test_scenes/PhysicsTest.blend --python export.py -- --output-file="assets/scenes/PhysicsTest.scn"

run:
	cargo run --example scenes
