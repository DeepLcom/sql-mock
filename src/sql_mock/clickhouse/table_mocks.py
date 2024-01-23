import json

import chdb

from sql_mock.table_mocks import BaseMockTable


class ClickHouseTableMock(BaseMockTable):
    _sql_dialect = "clickhouse"

    def __init__(
        self,
        *args,
        **kwargs,
    ):
        self.settings = None
        super().__init__(*args, **kwargs)

    def _get_results(self, query: str) -> list[dict]:
        res = chdb.query(query, "JSON")
        return json.loads(res.data()).get("data", [])
