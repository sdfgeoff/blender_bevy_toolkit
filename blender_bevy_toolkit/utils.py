import json

def jdict(**kwargs):
    """Dump arguments into a JSON-encoded string"""
    return json.dumps(dict(**kwargs))
