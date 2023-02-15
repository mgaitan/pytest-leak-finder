"""
this a similar demo with more tests to show the optimization done in
https://github.com/mgaitan/pytest-leak-finder/issues/4

The original algorithm take a lot more steps to find the leak.
"""
import pytest

l = []


@pytest.mark.parametrize("arg", range(10))
def test1(arg):
    assert True


def test2():
    l.append("leak")
    assert True


@pytest.mark.parametrize("arg", range(10))
def test3(arg):
    assert True


def test3():
    assert l == []
