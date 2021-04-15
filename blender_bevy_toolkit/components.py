import os

import bpy
import utils
from . import json_components
from . import component_base


def generate_component_list():
    """ Scans directories for components """
    component_base.COMPONENTS = []
    # Predefined json types
    
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
    

def load_folder(folder):
    json_components.load_folder(folder)
    load_python_components(folder)


def load_python_components(folder):
    import importlib.util
    
    filepaths = []
    for filename in os.listdir(folder):
        if filename.endswith(".py"):
            full_path = os.path.join(folder, filename)
            
            spec = importlib.util.spec_from_file_location(filename, full_path)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
