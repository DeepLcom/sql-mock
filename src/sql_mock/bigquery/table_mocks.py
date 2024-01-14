from google.cloud import bigquery

from sql_mock.bigquery.settings import BigQuerySettings
from sql_mock.table_mocks import BaseTableMock


class BigQueryTableMock(BaseTableMock):
    _sql_dialect = "bigquery"

    def __init__(
        self,
        *args,
        **kwargs,
    ):
        self.settings = BigQuerySettings()  # Note: This checks whether GOOGLE_APPLICATION_CREDENTIALS is set
        super().__init__(*args, **kwargs)

    def _get_results(self, query: str) -> list[dict]:
        client = bigquery.Client()  # Note this requires GOOGLE_APPLICATION_CREDENTIALS to be set
        query_job = client.query(query)
        return [dict(r) for r in query_job.result()]
