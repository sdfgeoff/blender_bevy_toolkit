class List:
    def __init__(self, *values):
        self.values = values
        
    def to_str(self):
       return  "[" + ",".join(encode(d) for d in self.values) + "]"
        
        
class Tuple:
    def __init__(self, *values):
        self.values = values
        
    def to_str(self):
        return "(" + ",".join(encode(d) for d in self.values) + ")"


class Str:
    def __init__(self, value):
        self.value = value

    def to_str(self):
        """repr a string with double quotes. This is probably a fragile
        hack, so if it breaks, please do something better!"""
        return '"' + repr("'" + self.value)[2:]


class Bool:
    def __init__(self, value):
        self.value = value
        
    def to_str(self):
        if self.value:
            return "true"
        else:
            return "false"


class Int:
    def __init__(self, value):
        self.value = value
        
    def to_str(self):
        return str(self.value)


class Float:
    def __init__(self, value):
        self.value = value
        
    def to_str(self):
        return str(self.value)
    
        
class Struct:
    def __init__(self, **mapping):
        self.mapping = mapping
        
    def to_str(self):
        field_string = ",".join(f"{k}:{encode(v)}" for k, v in self.mapping.items())
        return f"({field_string})"


class Map:
    def __init__(self, **mapping):
        self.mapping = mapping
        
    def to_str(self):
        field_string = ",".join(f"{encode(k)}:{encode(v)}" for k, v in self.mapping.items())
        return f"{{{field_string}}}"


class EnumValue:
    def __init__(self, variant, value=None):
        self.variant = variant
        self.value = value
        
    def to_str(self):
        if self.value is None:
            return self.variant
        return self.variant + encode(self.value)





def encode(data):
    """The "base" encoder. Call this with some data and hopefully it will be encoded
    as a string"""
    if hasattr(data, "to_str"):
        return data.to_str()
    return ENCODE_MAP[type(data)](data)


ENCODE_MAP = {
    str: Str,
    int: Int,
    bool: Bool,
    float: Float,
}

def encode(data):
    """The "base" encoder. Call this with some data and hopefully it will be encoded
    as a string"""
    if hasattr(data, "to_str"):
        return data.to_str()
    return ENCODE_MAP[type(data)](data).to_str()
