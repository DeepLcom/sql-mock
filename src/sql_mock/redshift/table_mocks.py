import redshift_connector

from sql_mock.redshift.settings import RedshiftSettings
from sql_mock.table_mocks import BaseTableMock


class RedshiftTableMock(BaseTableMock):
    _sql_dialect = "redshift"

    def __init__(
        self,
        *args,
        **kwargs,
    ):
        self.settings = RedshiftSettings()
        super().__init__(*args, **kwargs)

    def _get_results(self, query: str) -> list[dict]:
        with redshift_connector.connect(
            host=self.settings.host,
            database=self.settings.database,
            user=self.settings.user,
            password=self.settings.password,
            port=self.settings.port,
        ) as con:
            with con.cursor() as cursor:
                cursor.execute(query)
                res = cursor.fetch_dataframe()
        return res.to_dict("records")
