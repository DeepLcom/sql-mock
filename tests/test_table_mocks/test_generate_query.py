from textwrap import dedent

from sql_mock.column_mocks import ColumnMock
from sql_mock.table_mocks import BaseMockTable, table_meta


class IntTestColumn(ColumnMock):
    dtype = "Integer"


class StringTestColumn(ColumnMock):
    dtype = "String"


int_col = IntTestColumn(default=1)
string_col = StringTestColumn(default="hey")


@table_meta(table_ref="data.mock_test_table")
class MockTestTable(BaseMockTable):
    col1 = int_col
    col2 = string_col
    _sql_dialect = "bigquery"


# Test the _generate_query method
def test_generate_query_no_cte_provided(mocker):
    """Then the query should be generated with the provided query template"""
    # Arrange
    mock_table_instance = MockTestTable.from_dicts([])
    mock_table_instance._sql_mock_data.input_data = [mock_table_instance]
    original_query = f"SELECT * FROM {mock_table_instance._sql_mock_meta.table_ref}"
    cte_to_select = "some_cte"
    cte_adjusted_query = f"SELECT * FROM {cte_to_select}"
    dummy_return_query = "SELECT foo FROM bar"
    mock_table_instance._sql_mock_data.rendered_query = original_query

    mocked_select_from_cte = mocker.patch("sql_mock.table_mocks.select_from_cte", return_value=cte_adjusted_query)
    mocked_replace_original_table_references = mocker.patch(
        "sql_mock.table_mocks.replace_original_table_references", return_value=dummy_return_query
    )

    expected_query_template_result = dedent(
        f"""
    WITH {mock_table_instance._sql_mock_meta.cte_name} AS (
    \tSELECT cast('1' AS Integer) AS col1, cast('hey' AS String) AS col2 FROM (SELECT 1) WHERE FALSE
    ),

    result AS (
    \t{original_query}
    )

    SELECT
    \tcast(col1 AS Integer) AS col1,
    \tcast(col2 AS String) AS col2
    FROM result
    """
    )

    # Act
    query = mock_table_instance._generate_query()

    # Asserts
    mocked_select_from_cte.assert_not_called()
    mocked_replace_original_table_references.assert_called_once_with(
        expected_query_template_result, mock_tables=[mock_table_instance], dialect=mock_table_instance._sql_dialect
    )
    # The final query should be equal to whatever is returned by `replace_original_table_references`
    assert query == mocked_replace_original_table_references.return_value


def test_generate_query_cte_provided(mocker):
    """...then the query reference needs to be replaced to SELECT * FROM <cte>"""
    # Arrange
    mock_table_instance = MockTestTable.from_dicts([])
    mock_table_instance._sql_mock_data.input_data = [mock_table_instance]
    original_query = f"SELECT * FROM {mock_table_instance._sql_mock_meta.table_ref}"
    cte_to_select = "some_cte"
    cte_adjusted_query = f"SELECT * FROM {cte_to_select}"
    dummy_return_query = "SELECT foo FROM bar"
    mock_table_instance._sql_mock_data.rendered_query = original_query

    mocked_select_from_cte = mocker.patch("sql_mock.table_mocks.select_from_cte", return_value=cte_adjusted_query)
    mocked_replace_original_table_references = mocker.patch(
        "sql_mock.table_mocks.replace_original_table_references", return_value=dummy_return_query
    )

    expected_query_template_result = dedent(
        f"""
    WITH {mock_table_instance._sql_mock_meta.cte_name} AS (
    \tSELECT cast('1' AS Integer) AS col1, cast('hey' AS String) AS col2 FROM (SELECT 1) WHERE FALSE
    ),

    result AS (
    \t{cte_adjusted_query}
    )

    SELECT
    \t*
    FROM result
    """
    )

    # Act
    query = mock_table_instance._generate_query(cte_to_select=cte_to_select)

    # Asserts
    mocked_select_from_cte.assert_called_once_with(
        original_query, cte_to_select, sql_dialect=MockTestTable._sql_dialect
    )
    mocked_replace_original_table_references.assert_called_once_with(
        expected_query_template_result, mock_tables=[mock_table_instance], dialect=mock_table_instance._sql_dialect
    )
    # The final query should be equal to whatever is returned by `replace_original_table_references`
    assert query == mocked_replace_original_table_references.return_value
