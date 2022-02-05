""" Creates components from JSON files. This provides an easy
way for adding custom components without mucking around with python at all.

"""
import os
import json
import logging
from .utils import jdict
from .component_constructor import ComponentDefininition, FieldDefinition, component_from_def
from .component_base import register_component


logger = logging.getLogger(__name__)



def get_component_files(folder):
    """Looks for component definition files (.json) in the specified folder.
    Returns the path to these component files as an array"""
    component_definitions = []
    for filename in os.listdir(folder):
        if filename.endswith(".json"):
            component_definitions.append(os.path.join(folder, filename))
    return component_definitions


def parse_field(field):
    """Convert the json definition of a single field into something static"""
    return FieldDefinition(
        field=field["field"],
        type=field["type"],
        default=field["default"],
        description=field["description"],
    )




def construct_component_classes(component_filepath):
    """Parse the file from JSON into some python namedtuples"""
    logging.info(
        jdict(event="construct_json_classes", path=component_filepath, state="start")
    )

    try:
        with open(component_filepath, encoding="utf-8") as component_definition:
            component = json.load(component_definition)
    except json.decoder.JSONDecodeError as err:
        logging.exception(
            jdict(
                event="construct_json_component_parse_error",
                path=component_filepath,
                error=err,
                exc_info=err,
            )
        )
        return None

    component_def = ComponentDefininition(
        name=component["name"],
        description=component["description"],
        id=component["id"],
        struct=component["struct"],
        fields=[parse_field(f) for f in component["fields"]],
    )
    logging.debug(
        jdict(
            event="construct_json_classes",
            path=component_filepath,
            state="parse_complete",
        )
    )

    return component_from_def(component_def)

    


def load_folder(folder):
    """Scans a folder for json files and loads them as components"""
    logger.info(jdict(event="scan_folder_for_json_components", folder=folder))

    json_files = get_component_files(folder)
    logger.info(
        jdict(
            event="scan_folder_for_json_components",
            folder=folder,
            json_files=json_files,
        )
    )
    classes = [construct_component_classes(c) for c in json_files]
    for cls in classes:
        register_component(cls)
