from clickhouse_driver import Client

from sql_mock.clickhouse.settings import ClickHouseSettings
from sql_mock.table_mocks import BaseMockTable


class ClickHouseTableMock(BaseMockTable):
    def __init__(
        self,
        *args,
        **kwargs,
    ):
        self.settings = ClickHouseSettings()
        super().__init__(*args, **kwargs)

    def _get_results(self) -> list[dict]:
        query = self._generate_query()
        with Client(
            host=self.settings.host, user=self.settings.user, password=self.settings.password, port=self.settings.port
        ) as client:
            res = client.query_dataframe(query)
        return res.to_dict("records")
