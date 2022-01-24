BLENDER = blender


.PHONY: assets run fmt fmt-test

assets:
	rm -r assets || true
	$(BLENDER) -b test_scenes/Cube.blend --python export.py -- --output-file="assets/scenes/Cube.scn" --log-level=DEBUG
	$(BLENDER) -b test_scenes/PhysicsTest.blend --python export.py -- --output-file="assets/scenes/PhysicsTest.scn" --log-level=DEBUG
	$(BLENDER) -b test_scenes/Heirarchy.blend --python export.py -- --output-file="assets/scenes/Heirarchy.scn" --log-level=DEBUG

run:
	cargo run --example scenes -- scenes/PhysicsTest.scn

fmt:
	cargo fmt
	python -m black blender_bevy_toolkit
	
fmt-test:
	# Format
	cargo fmt --all --check
	python -m black --diff --check blender_bevy_toolkit
	
	# Linting python requires the blender environment
	blender -b --python-expr "from pylint.lint import Run; Run(['blender_bevy_toolkit'])"
	
	# Dead code check (python)
	python -m vulture --min-confidence 100 blender_bevy_toolkit
	
	
