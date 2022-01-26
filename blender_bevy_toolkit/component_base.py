from . import utils


class ComponentRepresentation:
    def __init__(self, typ, struct, type_override="struct"):
        self.typ = typ
        self.struct = struct
        self.type_override = type_override

    def to_str(self):
        return utils.encode({"type": self.typ, self.type_override: self.struct})

    def __repr__(self):
        return f"{self.typ} {{...}}"


COMPONENTS = []


def register_component(cls):
    global COMPONENTS
    COMPONENTS.append(cls)
    COMPONENTS.sort(key=lambda c: c.__name__)
    return cls
