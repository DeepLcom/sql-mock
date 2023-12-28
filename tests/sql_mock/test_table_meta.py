from sql_mock.table_mocks import BaseMockTable, table_meta


def test_query_path_provided(mocker):
    """...then the query should be read from the path and the result most be stored on the cls._sql_mock_data"""
    query = "SELECT bar FROM foo"
    query_path = "some_path"
    mock_open = mocker.patch("builtins.open")
    # Configure the mock to return the file content
    mock_open.return_value.__enter__.return_value.read.return_value = query

    @table_meta(table_ref="", query_path=query_path)
    class TestMock(BaseMockTable):
        pass

    assert TestMock._sql_mock_meta.query == query
    mock_open.assert_called_with(query_path)


def test_no_query_path_provided():
    """...then there should not be any query string stored on the cls._sql_mock_data"""

    @table_meta(table_ref="")
    class TestMock(BaseMockTable):
        pass

    assert TestMock._sql_mock_meta.query is None


def test_table_ref_provided():
    """...then the table_ref should be stored on the cls._sql_mock_data"""
    table_ref = "some.table"

    @table_meta(table_ref=table_ref)
    class TestMock(BaseMockTable):
        pass

    assert TestMock._sql_mock_meta.table_ref == table_ref
