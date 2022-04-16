# -*- coding: utf-8 -*-

from typing import TYPE_CHECKING, List, Optional

import pytest
from _pytest import nodes
from _pytest.config import Config
from _pytest.config.argparsing import Parser
from _pytest.main import Session
from _pytest.reports import TestReport

if TYPE_CHECKING:
    from _pytest.cacheprovider import Cache

CACHE_DIR = "cache/leak-finder"


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
        # Clear the list of failing tests if the plugin is not active.
        session.config.cache.set(CACHE_DIR, [])


class LeakFinderPlugin:
    def __init__(self, config: Config) -> None:
        self.config = config
        self.session: Optional[Session] = None
        self.report_status = ""
        assert config.cache is not None
        self.cache: Cache = config.cache
        self.lastfailed: Optional[str] = self.cache.get(CACHE_DIR, None)

    def pytest_sessionstart(self, session: Session) -> None:
        self.session = session

    def pytest_collection_modifyitems(
        self, config: Config, items: List[nodes.Item]
    ) -> None:
        if not self.lastfailed:
            self.report_status = "no previously failed tests, not skipping."
            return

        target = self.cache.get("cache/leakfinder-target", {})

        import ipdb

        ipdb.set_trace()
        # check all item nodes until we find a match on last failed
        failed_index = None
        for index, item in enumerate(items):
            if item.nodeid == self.lastfailed:
                failed_index = index
                break

        # If the previously failed test was not found among the test items,
        # do not skip any tests.
        if failed_index is None :
            self.report_status = "previously failed test not found, not skipping."
        else:
            # deselect group B
            total_target = items[:failed_index]
            group_A = items[:len(total_target)//2] 
            group_B = items[len(total_target)//2:-1]
        
            # deselect group B
            del items[len(total_target)//2:-1]
            import ipdb;ipdb.set_trace()
            
            # deselect group A
            # del items[:len(total_target)//2]
            config.hook.pytest_deselected(items=group_B)

            # TODO set in cache wich group we actually executed
            # if everything passes, we'll take the other group next run (plus the failed target)
            # if it fails, we split the group again

    def pytest_runtest_logreport(self, report: TestReport) -> None:
        if report.failed:
            # Mark test as the last failing and interrupt the test session.
            self.lastfailed = report.nodeid
            assert self.session is not None
            self.session.shouldstop = (
                "Test failed, continuing from this test next run."
            )

        elif report.when == "call":      # If the test was actually run and did pass.
            # Remove test from the failed ones, if exists.
            if report.nodeid == self.lastfailed:
                self.lastfailed = None

    def pytest_report_collectionfinish(self) -> Optional[str]:
        if self.config.getoption("verbose") >= 0 and self.report_status:
            return f"leakfinder: {self.report_status}"
        return None

    def pytest_sessionfinish(self) -> None:
        self.cache.set(CACHE_DIR, self.lastfailed)
