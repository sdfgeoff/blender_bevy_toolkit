""" In an ECS, a component is a piece of data about an entity. We
create these components from various properties in the blender object

each component is independant, so it can be defined in either a JSON
or pthon file. This file then goes and looks for these component
definitions.
"""
import os
import sys
import logging
import importlib.util

import bpy
from . import json_components
from . import component_base
from .utils import jdict

logger = logging.getLogger(__name__)


def generate_component_list():
    """Scans directories for components"""
    component_base.COMPONENTS = []
    # Predefined json types

    logger.info(jdict(event="generate_component_list", state="start"))

    here = os.path.dirname(os.path.abspath(__file__))

    load_folder(os.path.join(here, "core_definitions"))
    load_folder(os.path.join(here, "rapier_definitions"))

    try:
        blend_path = bpy.path.abspath("//")
    except AttributeError:
        # When blender initially loads the plugin, there is not open
        # blend file, so we can't do this. So we have to wait until the
        # file is opened.
        pass
    else:
        custom_component_folder = os.path.join(blend_path, "component_definitions")
        if os.path.isdir(custom_component_folder):
            load_folder(custom_component_folder)

    logger.info(jdict(event="generate_component_list", state="complete"))


def load_folder(folder):
    """Look for component defitions in a specific folder"""
    json_components.load_folder(folder)
    load_python_components(folder)


def load_python_components(folder):
    """Looks for python files in a folder. If they exist, load it as a module.

    Unfortunately loading a python module from a specific filepath is not a
    straightforward operation, so it is likely this will require revising for
    different versions of python and possibly differnet OS's"""
    logger.info(jdict(event="scan_folder_for_python_components", folder=folder))

    for filename in os.listdir(folder):
        if filename.endswith(".py"):
            module_name = os.path.splitext(filename)[0]
            full_path = os.path.join(folder, filename)

            logger.info(
                jdict(event="load_python_component", path=full_path, state="start")
            )

            spec = importlib.util.spec_from_file_location(module_name, full_path)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            sys.modules[module_name] = module

            logger.info(
                jdict(event="load_python_component", path=full_path, state="end")
            )