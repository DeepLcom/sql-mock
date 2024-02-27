from snowflake.connector import DictCursor, connect

from sql_mock.snowflake.settings import SnowflakeSettings
from sql_mock.table_mocks import BaseTableMock


class SnowflakeTableMock(BaseTableMock):
    _sql_dialect = "snowflake"

    def __init__(
        self,
        *args,
        **kwargs,
    ):
        self.settings = SnowflakeSettings()
        super().__init__(*args, **kwargs)

    def _get_results(self, query: str) -> list[dict]:
        with connect(
            user=self.settings.user,
            password=self.settings.password,
            account=self.settings.account,
        ) as conn:
            with conn.cursor(DictCursor) as cur:
                cur.execute(query)
                return cur.fetchall()
