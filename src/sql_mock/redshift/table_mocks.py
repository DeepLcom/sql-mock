import redshift_connector

from sql_mock.redshift.settings import RedshiftSettings
from sql_mock.table_mocks import BaseMockTable


class RedshiftMockTable(BaseMockTable):
    _sql_dialect = "redshift"

    def __init__(
        self,
        *args,
        **kwargs,
    ):
        self.settings = RedshiftSettings()
        super().__init__(*args, **kwargs)

    def _get_results(self, query: str) -> list[dict]:
        with redshift_connector.connect(**self.settings) as con:
            with con.cursor() as cursor:
                res = cursor.fetch_dataframe
        return res.to_dict("records")
