""" This script is useful as the basis of a CI setup using this exporter to
automatically export a bunch of files.

On the command line, call something like:
	blender -b test_scenes/Cube.blend --python export.py -- --output-file="bin/Cube.scn"
"""

import os
import sys
import bpy
import traceback
import argparse

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
import blender_bevy_toolkit


def export_all(args):
    parser = argparse.ArgumentParser()
    parser.add_argument('--output-file', help="Output all data to here", 
required=True)
    config = parser.parse_args(args)

    blender_bevy_toolkit.do_export({
        "output_filepath": config.output_file,
        "mesh_output_folder": "meshes",
        "make_duplicates_real": True
    })


def run_function_with_args(function):
    arg_pos = sys.argv.index('--') + 1
    try:
        function(sys.argv[arg_pos:])
    except:
        print("ERROR")
        traceback.print_exc()
        sys.exit(1)

    print("SUCCESS")
    sys.exit(0)


if __name__ == "__main__":
    run_function_with_args(export_all)
