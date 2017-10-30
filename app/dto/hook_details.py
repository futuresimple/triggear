import logging
from typing import Dict, Set

from app.enums.event_types import EventTypes


class HookDetails:
    def __str__(self) -> str:
        return f"HookDetails(" \
               f"eventType: {self.event_type}, " \
               f"repo: {self.repository}, " \
               f"branch: {self.branch}, " \
               f"sha: {self.sha}, " \
               f"tag: {self.tag}, " \
               f"changes: {self.changes}, " \
               f"query: {self.query})"

    def __init__(self, event_type: EventTypes, repository: str, branch: str, sha: str, **additional_queries):
        self.__event_type = event_type
        self.__repository: str = repository
        self.__branch: str = branch
        self.__sha: str = sha
        self.__tag: str = None
        self.__changes: Set[str] = set()
        self.__query: Dict[str, str] = dict(repository=repository, **additional_queries)
        logging.warning(str(self))

    def __eq__(self, other):
        return isinstance(other, HookDetails) and \
            self.event_type == other.event_type and \
            self.changes == other.changes and \
            self.repository == other.repository and \
            self.tag == other.tag and \
            self.sha == other.sha and \
            self.branch == other.branch and \
            self.query == other.query

    def __ne__(self, other):
        return not (self == other)

    @property
    def event_type(self):
        return self.__event_type

    @property
    def repository(self) -> str:
        return self.__repository

    @property
    def branch(self) -> str:
        return self.__branch

    @property
    def sha(self) -> str:
        return self.__sha

    @property
    def query(self) -> dict:
        return self.__query

    @property
    def tag(self) -> str:
        return self.__tag

    @tag.setter
    def tag(self, value: str):
        self.__tag = value

    @property
    def changes(self) -> Set[str]:
        return self.__changes

    @changes.setter
    def changes(self, value: Set[str]):
        self.__changes = value