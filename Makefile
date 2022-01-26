BLENDER = blender


.PHONY: assets run fmt fmt-test ref-assets

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
	# blender -b --python-expr "from pylint.lint import Run; Run(['blender_bevy_toolkit'])"
	
	# Dead code check (python)
	python -m vulture --min-confidence 100 blender_bevy_toolkit
	
	
ref-assets:
	# Delete existing ref-assets
	rm -r ref-assets  || true
	
	# Store current assets somewhere safe
	mv assets assets-bak || true
	
	# Make new assets from scratch
	$(MAKE) assets
	
	# Store new assets as ref-assets
	mv assets ref-assets
	
	# Restore current assets
	mv assets-bak assets
	

diff-test: assets
	# Check for changes against the files in ref-assets. This allows seeing what impact a PR has by forcing output changes to show up in the commit
	# To update the reference assets run `make ref-assets`
	diff --recursive assets ref-assets
