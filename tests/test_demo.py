l = []

def test1():
    assert True


def test2():
    assert True


def test3():
    global l
    l.append("leak")
    assert True


def test4():
    assert True


def test5():
    assert l == []


def test6():
    assert True
