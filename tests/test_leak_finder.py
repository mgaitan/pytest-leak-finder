# -*- coding: utf-8 -*-
import pytest
from pytest_leak_finder import bizect


@pytest.fixture
def module_with_a_leaking_test(testdir):
    testdir.makepyfile(
        """
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
    """
    )


def test_first_run_set_target(testdir, module_with_a_leaking_test):
    result = testdir.runpytest("--leak-finder", "-v")
    result.stdout.fnmatch_lines(
        [
            "test_first_run_set_target.py::test5 FAILED*",
            "Target set to: test_first_run_set_target.py::test5",
            "Next step: a",
        ]
    )
    assert result.ret == 2


def test_second_passed(testdir, module_with_a_leaking_test):
    testdir.runpytest("--leak-finder")
    result = testdir.runpytest("--leak-finder", "-v")
    result.stdout.fnmatch_lines(
        [
            "test_second_passed.py::test5 PASSED*",
            "We reach the target and nothing failed. Let's change the last half.",
            "Next step: ba",
        ]
    )
    assert result.ret == 0


def test_3rd_run_set_target(testdir, module_with_a_leaking_test):
    testdir.runpytest("--leak-finder")
    testdir.runpytest("--leak-finder")
    result = testdir.runpytest("--leak-finder", "-v")

    result.stdout.fnmatch_lines(
        [
            "test_3rd_run_set_target.py::test3 PASSED*",
            "test_3rd_run_set_target.py::test5 FAILED*",
            "We found a leak!",
            "Leak found in: test_3rd_run_set_target.py::test3",
            "Last step was: ba",
        ]
    )
    assert result.ret == 1


@pytest.mark.parametrize(
    "steps, expected",
    [
        ("a", [0, 1, 2, 3, 4, 9]),
        ("aa", [0, 1, 2, 9]),
        ("aaa", [0, 1, 9]),
        ("aaaa", [0, 9]),
        ("aaaaa", [0, 9]),
        ("b", [5, 6, 7, 8, 9]),
        ("ba", [5, 6, 9]),
        ("baa", [5, 9]),
        ("baa", [5, 9]),
        ("bab", [6, 9]),
        ("bb", [7, 8, 9]),
        ("bba", [7, 9]),
        ("bbb", [8, 9]),
    ],
)
def test_bizect(steps, expected):
    assert bizect(list(range(10)), steps=steps) == expected
