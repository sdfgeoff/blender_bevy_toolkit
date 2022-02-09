from . import ron


def test_str():
    assert ron.encode(ron.Str("asdf")) == '"asdf"'
    assert ron.encode("asdf") == '"asdf"'
    assert ron.encode("'qwer") == '"\'qwer"'


def test_int():
    assert ron.encode(ron.Int(1234)) == "1234"
    assert ron.encode(2345) == "2345"


def test_float():
    assert ron.encode(ron.Float(12.34)) == "12.34"
    assert ron.encode(23.45) == "23.45"


def test_bool():
    assert ron.encode(ron.Bool(True)) == "true"
    assert ron.encode(False) == "false"


def test_list():
    assert ron.encode(ron.List()) == "[]"
    assert ron.encode(ron.List("A", "B", 2)) == '["A","B",2]'


def test_tuple():
    assert ron.encode(ron.Tuple()) == "()"
    assert ron.encode(ron.Tuple("A", "B", 1)) == '("A","B",1)'


def test_struct():
    assert ron.encode(ron.Struct(asdf="qwer")) == '(asdf:"qwer")'
    assert ron.encode(ron.Struct(asdf=ron.Tuple(1, 2))) == "(asdf:(1,2))"


def test_map():
    assert ron.encode(ron.Map(asdf="qwer")) == '{"asdf":"qwer"}'
    assert ron.encode(ron.Map(asdf=ron.Tuple(1, 2))) == '{"asdf":(1,2)}'


def test_enumvalue():
    assert ron.encode(ron.EnumValue("Click")) == "Click"
    assert ron.encode(ron.EnumValue("Click", ron.Tuple(1, 2))) == "Click(1,2)"
    assert ron.encode(ron.EnumValue("Some", ron.Tuple("Value"))) == 'Some("Value")'
    assert ron.encode(ron.EnumValue("None")) == "None"
