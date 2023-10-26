import sql_mock.bigquery.column_mocks as col
from sql_mock.bigquery.table_mocks import BigQueryMockTable
from sql_mock.table_mocks import table_meta


@table_meta(table_ref="data.data_geeks")
class DataGeeks(BigQueryMockTable):
    data_geek_id = col.Int(default=1)
    name = col.String(default="Data Geek")


@table_meta(table_ref="data.meetup_visits")
class MeetupVisits(BigQueryMockTable):
    data_geek_id = col.Int(default=1)
    date = col.Date(default="2023-10-26")


@table_meta(table_ref="data.visit_counts")
class VisitCounts(BigQueryMockTable):
    data_geek_id = col.Int(default=1)
    name = col.String(default="Data Geek")
    visit_count = col.Int(default=0)
