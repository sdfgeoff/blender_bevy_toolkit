import os
import sys
import argparse
import traceback
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import bpy
import struct
import hashlib


from blender_bevy_toolkit import utils, components, component_base


class Entity:
    def __init__(self, id, comp):
        self.id = id
        self.components = comp
    
    def to_str(self):
        return "(\n    entity: {},\n    components:{}\n)".format(
            utils.encode(self.id), 
            utils.iterable_to_string(self.components, "[\n        ", "\n    ]", ",\n        ")
        )


def export_entity(config, obj, id):
    entity = Entity(id, list())

    for component in component_base.COMPONENTS:
        if component.is_present(obj):
            new_component = component.encode(config, obj)
            assert isinstance(new_component, component_base.ComponentRepresentation), "Component {} did not return ComponentDefinition".format(component)
            entity.components.append(new_component)
    
    return entity




def export_all(args):
    parser = argparse.ArgumentParser()
    parser.add_argument('--output-folder', help="Output all data to here", required=True)
    config = parser.parse_args(args)
    
    blend_name = os.path.basename(bpy.data.filepath)
    output_folder = config.output_folder
    print("Exporting to", output_folder)
    
    # Make all collections into their real objects. Ideally one day this
    # will be subbed for actually using proper instancing of collections
    # but I couldn't get this to work in bevy :(
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.duplicates_make_real(use_base_parent=True, use_hierarchy=False)
    
    mesh_output_folder = os.path.join(output_folder, "Meshes")
    if not os.path.exists(mesh_output_folder):
        os.makedirs(mesh_output_folder)
    
    collection_output_folder = os.path.join(output_folder, "Collections")
    if not os.path.exists(collection_output_folder):
        os.makedirs(collection_output_folder)
    
    
    config = {
        "blend_name": blend_name,
        "output_folder": output_folder,
        "mesh_output_folder": mesh_output_folder,
        "collection_output_folder": collection_output_folder,
    }

    for collection in bpy.data.collections:
        if collection.library is not None:
            # Ignore external libraries
            continue
        
        config["collection"] = collection
        collection_output_file = os.path.join(collection_output_folder, "{}.scn".format(
            collection.name,
        ))
        
        objects = [o for o in collection.objects]
        entities = [export_entity(config, o, i) for i, o in enumerate(objects)]
        collection_data = entities
        
        open(collection_output_file, "w").write(utils.encode(entities))
    
        

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

