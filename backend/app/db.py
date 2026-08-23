"""
Thin wrapper around the official neo4j driver.

CognoDB speaks openCypher over Bolt, so the standard neo4j Python driver
works unmodified — no custom SDK needed.
"""
import logging
from contextlib import contextmanager
from typing import Any, Iterator, Optional

from neo4j import GraphDatabase, basic_auth
from neo4j.exceptions import AuthError, ServiceUnavailable

from .config import settings

logger = logging.getLogger("contextgraph.db")


class Database:
    def __init__(self) -> None:
        self._driver = None

    def connect(self):
        if self._driver is None:
            self._driver = GraphDatabase.driver(
                settings.COGNODB_URI,
                auth=basic_auth(settings.COGNODB_USER, settings.COGNODB_PASSWORD),
            )
        return self._driver

    def close(self) -> None:
        if self._driver is not None:
            self._driver.close()
            self._driver = None

    def verify_connectivity(self) -> tuple[bool, Optional[str]]:
        """Used by /health — never raises, always returns a status tuple."""
        try:
            self.connect().verify_connectivity()
            return True, None
        except (ServiceUnavailable, AuthError) as exc:
            logger.error("CognoDB connectivity check failed: %s", exc)
            return False, str(exc)
        except Exception as exc:  # pragma: no cover - defensive catch-all
            logger.error("Unexpected error checking CognoDB: %s", exc)
            return False, str(exc)

    @contextmanager
    def session(self) -> Iterator[Any]:
        driver = self.connect()
        session = driver.session()
        try:
            yield session
        finally:
            session.close()


db = Database()


def run_query(cypher: str, params: Optional[dict] = None) -> list[dict]:
    """Run a parameterized read/write query and return records as plain dicts."""
    with db.session() as session:
        result = session.run(cypher, params or {})
        return [record.data() for record in result]
