
.PHONY: assets

assets:
	rm -r assets || true
	blender -b test_scenes/Cube.blend --python export.py -- --output-file="assets/scenes/Cube.scn" --log-level=DEBUG
	blender -b test_scenes/PhysicsTest.blend --python export.py -- --output-file="assets/scenes/PhysicsTest.scn" --log-level=DEBUG

run:
	cargo run --example scenes
