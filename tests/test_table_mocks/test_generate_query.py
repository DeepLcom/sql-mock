import sqlglot

from sql_mock.column_mocks import BaseColumnMock
from sql_mock.table_mocks import BaseTableMock, table_meta


class IntTestColumn(BaseColumnMock):
    dtype = "Integer"


class StringTestColumn(BaseColumnMock):
    dtype = "String"


int_col = IntTestColumn(default=1)
string_col = StringTestColumn(default="hey")


@table_meta(table_ref="data.mock_test_table")
class MockTestTable(BaseTableMock):
    col1 = int_col
    col2 = string_col
    _sql_dialect = "bigquery"


# Test the _generate_query method
def test_generate_query_no_cte_provided(mocker):
    """Then the query should be generated with the provided query template"""
    # Arrange
    table_mock_instance = MockTestTable.from_dicts([])
    table_mock_instance._sql_mock_data.input_data = [table_mock_instance]
    original_query = f"SELECT * FROM {table_mock_instance._sql_mock_meta.table_ref}"
    dummy_return_query = sqlglot.parse_one("SELECT foo FROM bar")
    table_mock_instance._sql_mock_data.rendered_query = original_query

    mocked_select_from_cte = mocker.patch("sql_mock.table_mocks.select_from_cte")
    mocked_replace_original_table_references = mocker.patch(
        "sql_mock.table_mocks.replace_original_table_references", return_value=dummy_return_query
    )

    expected_query_template_result = sqlglot.parse_one(
        f"""
    WITH {table_mock_instance._sql_mock_meta.cte_name} AS (
    \tSELECT cast('1' AS Integer) AS col1, cast('hey' AS String) AS col2 FROM (SELECT 1) WHERE FALSE
    ),

    result AS (
    {original_query}
    )

    SELECT
    cast(col1 AS Integer) AS col1,
    cast(col2 AS String) AS col2
    FROM result
    """
    )

    # Act
    query = table_mock_instance._generate_query()

    # Asserts
    mocked_select_from_cte.assert_not_called()
    mocked_replace_original_table_references.assert_called_once_with(
        query_ast=expected_query_template_result,
        table_ref=table_mock_instance._sql_mock_meta.table_ref,
        sql_mock_cte_name=table_mock_instance._sql_mock_meta.cte_name,
        dialect=table_mock_instance._sql_dialect
    )
    # The final query should be equal to whatever is returned by `replace_original_table_references`
    assert query == mocked_replace_original_table_references.return_value.sql(pretty=True)


def test_generate_query_cte_provided(mocker):
    """...then the query reference needs to be replaced to SELECT * FROM <cte>"""
    # Arrange
    table_mock_instance = MockTestTable.from_dicts([])
    table_mock_instance._sql_mock_data.input_data = [table_mock_instance]
    original_query = f"SELECT * FROM {table_mock_instance._sql_mock_meta.table_ref}"
    cte_to_select = "some_cte"
    cte_adjusted_query = f"SELECT * FROM {cte_to_select}"
    dummy_return_query = sqlglot.parse_one("SELECT foo FROM bar")
    table_mock_instance._sql_mock_data.rendered_query = original_query

    mocked_select_from_cte = mocker.patch("sql_mock.table_mocks.select_from_cte", return_value=cte_adjusted_query)
    mocked_replace_original_table_references = mocker.patch(
        "sql_mock.table_mocks.replace_original_table_references", return_value=dummy_return_query
    )

    expected_query_template_result = sqlglot.parse_one(
        f"""
    WITH {table_mock_instance._sql_mock_meta.cte_name} AS (
    \tSELECT cast('1' AS Integer) AS col1, cast('hey' AS String) AS col2 FROM (SELECT 1) WHERE FALSE
    ),

    result AS (
    {cte_adjusted_query}
    )

    SELECT
    *
    FROM result
    """
    )

    # Act
    query = table_mock_instance._generate_query(cte_to_select=cte_to_select)

    # Asserts
    mocked_select_from_cte.assert_called_once_with(
        original_query, cte_to_select, sql_dialect=table_mock_instance._sql_dialect
    )
    # replace_original_table_references should be called once since we have a single input table
    mocked_replace_original_table_references.assert_called_once_with(
        query_ast=expected_query_template_result,
        table_ref=table_mock_instance._sql_mock_meta.table_ref,
        sql_mock_cte_name=table_mock_instance._sql_mock_meta.cte_name,
        dialect=table_mock_instance._sql_dialect
    )
    # The final query should be equal to whatever is returned by `replace_original_table_references`
    assert query == mocked_replace_original_table_references.return_value.sql(pretty=True)


def test_generate_query_sql_has_semicolon():
    """...then the query should not break sql mock"""
    # Arrange
    table_mock_instance = MockTestTable.from_dicts([])
    table_mock_instance._sql_mock_data.input_data = [table_mock_instance]
    original_query = f"SELECT * FROM {table_mock_instance._sql_mock_meta.table_ref};"
    table_mock_instance._sql_mock_data.rendered_query = original_query

    # Act
    table_mock_instance._generate_query()
