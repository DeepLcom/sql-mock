from sql_mock.clickhouse.column_mocks import Int
from sql_mock.clickhouse.table_mocks import ClickHouseTableMock
from sql_mock.table_mocks import table_meta


@table_meta(table_ref="mock_test_table")
class MockTestTable(ClickHouseTableMock):
    id = Int(default=1)


def test_get_results(mocker):
    """
    Test the _get_results method.
    """
    mock_query_result = [{"column1": "value1", "column2": 42}]
    query = "SELECT 'value1' as column1, 42 as column2"

    instance = ClickHouseTableMock()
    result = instance._get_results(query=query)

    assert result == mock_query_result
