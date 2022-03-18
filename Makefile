.SUFFIXES:

BLENDER = .blender/blender


.PHONY: assets run fmt fmt-test ref-assets

assets:
	rm -r assets/scenes || true
	$(BLENDER) -b test_scenes/Cube.blend --python ./scripts/export.py --python-exit-code=1  -- --output-file="assets/scenes/Cube.scn" --log-level=DEBUG
	$(BLENDER) -b test_scenes/PhysicsTest.blend --python ./scripts/export.py --python-exit-code=1   -- --output-file="assets/scenes/PhysicsTest.scn" --log-level=DEBUG
	$(BLENDER) -b test_scenes/Heirarchy.blend --python ./scripts/export.py --python-exit-code=1   -- --output-file="assets/scenes/Heirarchy.scn" --log-level=DEBUG
	$(BLENDER) -b test_scenes/Lights.blend --python ./scripts/export.py --python-exit-code=1   -- --output-file="assets/scenes/Lights.scn" --log-level=DEBUG
	$(BLENDER) -b test_scenes/Camera.blend --python ./scripts/export.py --python-exit-code=1   -- --output-file="assets/scenes/Camera.scn" --log-level=DEBUG
	$(BLENDER) -b test_scenes/Materials.blend --python ./scripts/export.py --python-exit-code=1   -- --output-file="assets/scenes/Materials.scn" --log-level=DEBUG

run:
	cargo run --example scenes

fmt:
	cargo fmt
	python -m black blender_bevy_toolkit
	
fmt-test:
	# Format
	cargo fmt --all --check
	python -m black --diff --check blender_bevy_toolkit
	
	# Linting python requires the blender environment
	$(BLENDER) -b --python ./scripts/pylint_in_blender.py --python-exit-code=1
	
	# Dead code check (python)
	python -m vulture --min-confidence 100 blender_bevy_toolkit

test:
	$(BLENDER) -b --python ./scripts/pytest_in_blender.py --python-exit-code=1
	cargo test
	
	
	
	
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
	diff --recursive assets/scenes ref-assets/scenes


# Version of blender for testing
.blender/blender-3.0.0-linux-x64.tar.xz:
	mkdir -p .blender
	# Downloading blender
	cd .blender; wget -nv https://mirror.clarkson.edu/blender/release/Blender3.0/blender-3.0.0-linux-x64.tar.xz; 
	
.blender/blender: .blender/blender-3.0.0-linux-x64.tar.xz
	# Extracting blender
	cd .blender; tar -xf blender-3.0.0-linux-x64.tar.xz
	cd .blender; touch blender-3.0.0-linux-x64/blender 
	cd .blender; ln -s blender-3.0.0-linux-x64/blender blender  || true
	
	$(BLENDER) -b --python ./scripts/install_test_deps_in_blender.py

.PHONY: .blender/blender

blender: .blender/blender
