import os

import pytest

from sql_mock.clickhouse import column_mocks as col
from sql_mock.clickhouse.table_mocks import ClickHouseTableMock
from sql_mock.table_mocks import table_meta

pytestmark = pytest.mark.integration


@pytest.fixture(autouse=True)
def set_env():
    if not os.getenv("SQL_MOCK_CLICKHOUSE_HOST"):
        os.environ["SQL_MOCK_CLICKHOUSE_HOST"] = "localhost"
    if not os.getenv("SQL_MOCK_CLICKHOUSE_PORT"):
        os.environ["SQL_MOCK_CLICKHOUSE_PORT"] = "8123"
    if not os.getenv("SQL_MOCK_CLICKHOUSE_USER"):
        os.environ["SQL_MOCK_CLICKHOUSE_USER"] = "default"
    if not os.getenv("SQL_MOCK_CLICKHOUSE_PASSWORD"):
        os.environ["SQL_MOCK_CLICKHOUSE_PASSWORD"] = ""


def test_simple_query():
    query = """SELECT
        user_id,
        count() AS sessions
    FROM sessions
    GROUP BY user_id
    """

    @table_meta(table_ref="sessions")
    class SessionsMock(ClickHouseTableMock):
        user_id = col.String(default="foo")

    @table_meta(query=query)
    class ResultMock(ClickHouseTableMock):
        user_id = col.String(default="foo")
        sessions = col.Int(default=0)

    sessions_mock = SessionsMock.from_dicts(
        [
            {"user_id": "a"},
            {"user_id": "a"},
            {"user_id": "a"},
            {"user_id": "b"},
        ],
    )

    result = ResultMock.from_mocks(input_data=[sessions_mock])

    expected = [
        {"user_id": "a", "sessions": 3},
        {"user_id": "b", "sessions": 1},
    ]

    result.assert_equal(expected)
