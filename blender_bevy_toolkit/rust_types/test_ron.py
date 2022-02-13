""" Test that ron.py produces valid RON """
from . import ron


ron.INDENT_SIZE = 0


def test_str():
    """Check that a string gets quotes put around it correctly"""
    assert ron.encode(ron.Str("asdf")) == '"asdf"'
    assert ron.encode("asdf") == '"asdf"'
    assert ron.encode("'qwer") == '"\'qwer"'


def test_int():
    """Numbers should be bare numbers"""
    assert ron.encode(ron.Int(1234)) == "1234"
    assert ron.encode(2345) == "2345"


def test_float():
    """Numbers should be bare numbers"""
    assert ron.encode(ron.Float(12.34)) == "12.34"
    assert ron.encode(23.45) == "23.45"


def test_bool():
    """Bools are lower case"""
    assert ron.encode(ron.Bool(True)) == "true"
    assert ron.encode(False) == "false"


def test_list():
    """Lists serizlize internals and are square brackets"""
    assert ron.encode(ron.List()) == "[]"
    assert ron.encode(ron.List("A", "B", 2)) == '["A","B",2]'


def test_tuple():
    """Tuples serizlize internals and are round brackets"""
    assert ron.encode(ron.Tuple()) == "()"
    assert ron.encode(ron.Tuple("A", "B", 1)) == '("A","B",1)'


def test_struct():
    """Struct is round brakcets and doesn't quote keys"""
    assert ron.encode(ron.Struct(asdf="qwer")) == '(asdf:"qwer")'
    assert ron.encode(ron.Struct(asdf=ron.Tuple(1, 2))) == "(asdf:(1,2))"


def test_map():
    """Maps are curly-braces and quote keys"""
    assert ron.encode(ron.Map(asdf="qwer")) == '{"asdf":"qwer"}'
    assert ron.encode(ron.Map(asdf=ron.Tuple(1, 2))) == '{"asdf":(1,2)}'


def test_enumvalue():
    """EnumValue is a name followed by it's value. The value is
    surrounded by round brakcets (if tuple) or curly braces (if struct)"""
    assert ron.encode(ron.EnumValue("Click")) == "Click"
    assert ron.encode(ron.EnumValue("Click", ron.Tuple(1, 2))) == "Click(1,2)"
    assert ron.encode(ron.EnumValue("Some", ron.Tuple("Value"))) == 'Some("Value")'
    assert ron.encode(ron.EnumValue("None")) == "None"
