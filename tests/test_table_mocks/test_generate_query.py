from textwrap import dedent

import pytest
import sqlglot

from sql_mock.column_mocks import ColumnMock
from sql_mock.table_mocks import BaseMockTable, replace_original_table_references, select_from_cte, table_meta


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


def test_replace_original_table_references_when_reference_exists():
    """...then the original table reference should be replaced with the mocked table reference"""
    query = f"SELECT * FROM {MockTestTable._sql_mock_meta.table_ref}"
    mock_tables = [MockTestTable()]
    expected = "SELECT * FROM data__mock_test_table"
    assert expected == replace_original_table_references(query, mock_tables)


def test_replace_original_table_references_when_reference_does_not_exist():
    """...then the original reference should not be replaced"""
    query = "SELECT * FROM some_table"
    mock_tables = [MockTestTable()]
    expected = "SELECT * FROM some_table"
    assert expected == replace_original_table_references(query, mock_tables)


def test_select_from_cte_when_cte_exists():
    """...then the final select of the query should be replaced with a select from the cte"""
    cte_name = "cte_1"
    query = """
    WITH cte_1 AS (
      SELECT * FROM some_table
    ),
    cte_2 AS (
      SELECT a, b
      FROM cte
      WHERE a = 'foo'
    )

    SELECT a, b, * FROM cte_2
    """

    expected = sqlglot.parse_one(
        """
    WITH cte_1 AS (
      SELECT * FROM some_table
    ),
    cte_2 AS (
      SELECT a, b
      FROM cte
      WHERE a = 'foo'
    )

    SELECT * FROM cte_1
    """
    )
    # Make sure we match the query format
    expected = expected.sql(pretty=True)

    assert expected == select_from_cte(query, cte_name)


def test_select_from_cte_when_cte_does_not_exist():
    """...then the method should raise a ValueError"""
    cte_name = "cte_1"
    query = """
    WITH cte_2 AS (
      SELECT a, b
      FROM cte
      WHERE a = 'foo'
    )

    SELECT * FROM cte_2
    """

    with pytest.raises(ValueError):
        select_from_cte(query, cte_name)


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
    WITH {mock_table_instance._sql_mock_meta.table_ref} AS (
    \tSELECT cast('1' AS Integer) AS col1, cast('hey' AS String) AS col2 WHERE FALSE
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
        expected_query_template_result, mock_tables=[mock_table_instance]
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
    WITH {mock_table_instance._sql_mock_meta.table_ref} AS (
    \tSELECT cast('1' AS Integer) AS col1, cast('hey' AS String) AS col2 WHERE FALSE
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
    mocked_select_from_cte.assert_called_once_with(original_query, cte_to_select)
    mocked_replace_original_table_references.assert_called_once_with(
        expected_query_template_result, mock_tables=[mock_table_instance]
    )
    # The final query should be equal to whatever is returned by `replace_original_table_references`
    assert query == mocked_replace_original_table_references.return_value
