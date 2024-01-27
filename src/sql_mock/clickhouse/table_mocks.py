import clickhouse_connect

from sql_mock.clickhouse.settings import ClickHouseSettings
from sql_mock.table_mocks import BaseTableMock


class ClickHouseTableMock(BaseTableMock):
    _sql_dialect = "clickhouse"

    def __init__(
        self,
        *args,
        **kwargs,
    ):
        self.settings = ClickHouseSettings()
        super().__init__(*args, **kwargs)

    def _get_results(self, query: str) -> list[dict]:
        with clickhouse_connect.get_client(
            host=self.settings.host,
            secure=self.settings.use_secure_connection,
            username=self.settings.user,
            password=self.settings.password,
            port=self.settings.port,
        ) as client:
            res = client.query(query, use_none=True)
        return [dict(zip(res.column_names, row)) for row in res.result_rows]
