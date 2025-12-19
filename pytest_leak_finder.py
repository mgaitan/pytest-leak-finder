from typing import TYPE_CHECKING, List, Optional

import pytest
from _pytest import nodes
from _pytest.config import Config
from _pytest.config.argparsing import Parser
from _pytest.main import Session
from _pytest.reports import TestReport

if TYPE_CHECKING:
    from _pytest.cacheprovider import Cache
    from _pytest.terminal import TerminalReporter

CACHE_NAME = "cache/leakfinder"


def pytest_addoption(parser: Parser) -> None:
    group = parser.getgroup("general")
    group.addoption(
        "--leak-finder",
        action="store_true",
        default=False,
        dest="leakfinder",
        help="Bisect previous passed tests until find one that fail",
    )


@pytest.hookimpl
def pytest_configure(config: Config) -> None:
    if config.getoption("leakfinder"):
        config.pluginmanager.register(LeakFinderPlugin(config), "leakfinderplugin")


def pytest_sessionfinish(session: Session) -> None:
    if not session.config.getoption("leakfinder"):
        assert session.config.cache is not None
        # Clear the cache if the plugin is not active.
        session.config.cache.set(CACHE_NAME, {"steps": "", "target": None})


def bizect(items, steps="a"):
    """
    given a list, select the a/b n-th group plus the last element

    >>> items = list(range(10))
    >>> bizect(items)
    [0, 1, 2, 3, 4, 9]
    >>> bizect(items, steps="b")
    [5, 6, 7, 8, 9]
    >>> bizect(items, "ba")
    [5, 6, 9]
    >>> bizect(items, "bb")
    [7, 8, 9]
    """
    r = items.copy()
    for key in steps:
        if key == "a":
            r = r[: len(r) // 2]
        else:
            r = r[len(r) // 2 : -1]
        r += [items[-1]]
    return r


class LeakFinderPlugin:
    def __init__(self, config: Config) -> None:
        self.config = config
        self.session: Optional[Session] = None
        self.report_status = ""
        self.cache: Cache = config.cache
        self.previous = self.cache.get(CACHE_NAME, {"steps": "", "target": None})
        self.target = self.previous.get("target")

    def pytest_sessionstart(self, session: Session) -> None:
        self.session = session
        self.msg_to_report = None
        self.leak_candidate = None

    def pytest_collection_modifyitems(
        self, config: Config, items: List[nodes.Item]
    ) -> None:
        if not self.target:
            self.report_status = "no previously failed tests, not skipping."
            return

        # check all item nodes until we find a match on last failed
        failed_index = None
        for index, item in enumerate(items):
            if item.nodeid == self.target:
                failed_index = index
                break

        # If the previously failed test was not found among the test items,
        # do not skip any tests.
        if failed_index:
            new_items = bizect(items[: failed_index + 1], steps=self.previous["steps"])
            deselected = set(items) - set(new_items)
            items[:] = new_items
            self.leak_candidate = items[0].nodeid if len(items) == 2 else None
            config.hook.pytest_deselected(items=deselected)

    def pytest_runtest_logreport(self, report: TestReport) -> None:
        if not self.previous["steps"] and report.failed:
            # the first fail on the first run set the target
            self.previous["target"] = report.nodeid
            self.previous["steps"] += "a"
            if self.session is not None:
                self.session.shouldstop = True
            self.msg_to_report = f"Target set to: {report.nodeid}"
        elif report.nodeid == self.previous["target"] and report.when == "call":
            if report.failed and self.leak_candidate:
                self.msg_to_report = "We found a leak!"
            elif report.failed:
                self.msg_to_report = (
                    "The group selected still fails. Let's do a new partition."
                )
                self.previous["steps"] += "a"
            else:
                self.msg_to_report = "We reach the target and nothing failed. Let's change the last half."
                last = self.previous["steps"][-1]
                self.previous["steps"] = (
                    self.previous["steps"][:-1] + "ba" if last == "a" else "aa"
                )

    def pytest_terminal_summary(self, terminalreporter: "TerminalReporter") -> None:
        tr = terminalreporter
        if self.msg_to_report:
            tr.write_sep("=", "Leak finder")
            tr.write_line(self.msg_to_report + "\n")
            if self.leak_candidate:
                tr.write_line(f"Leak found in: {self.leak_candidate}")
                tr.write_line(f"Last step was: {self.previous['steps']}")
            else:
                tr.write_line(f"Next step: {self.previous['steps']}")
                tr.write_line(f"Current target is: {self.previous['target']}")

    def pytest_sessionfinish(self) -> None:
        self.cache.set(CACHE_NAME, self.previous)
