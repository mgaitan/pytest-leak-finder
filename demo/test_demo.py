# this module is exclude from CI colecctions

leak_state = []


def test1():
    assert True


def test2():
    assert True


def test3():
    global leak_state
    leak_state.append("leak")
    assert True


def test4():
    assert True


def test5():
    assert leak_state == []


def test6():
    assert True
