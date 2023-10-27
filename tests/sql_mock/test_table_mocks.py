from textwrap import dedent

import pytest

from sql_mock.column_mocks import ColumnMock
from sql_mock.exceptions import ValidationError
from sql_mock.table_mocks import BaseMockTable, table_meta


class IntTestColumn(ColumnMock):
    dtype = "Integer"


class StringTestColumn(ColumnMock):
    dtype = "String"


int_col = IntTestColumn(default=1)
string_col = StringTestColumn(default="hey")


@table_meta(table_ref="mock_test_table")
class MockTestTable(BaseMockTable):
    col1 = int_col
    col2 = string_col


# Create a fixture for an instance of BaseMockTable
@pytest.fixture
def base_mock_table_instance():
    @table_meta(table_ref="base_mock_table")
    class MockTable(BaseMockTable):
        pass

    return MockTable()


# Test the __init__ method
def test_init():
    instance = MockTestTable()
    assert instance.SQLMockData.columns == {"col1": int_col, "col2": string_col}
    assert instance.SQLMockData.data == []


def test_wrong_fields_prodivded_to_model():
    """...then it should raise a validation error"""
    with pytest.raises(ValueError):
        MockTestTable(data=[{"not_existing_key": 1}])


# Test the from_inputs method
def test_from_inputs(mocker, base_mock_table_instance):
    query = "SELECT * FROM some_table"
    input_data = [base_mock_table_instance]
    query_template_kwargs = {}

    # Mock the _get_results method to return a simple list of dicts
    expected_results = [{"column1": 1, "column2": "value1"}, {"column1": 2, "column2": "value2"}]
    mocker.patch.object(BaseMockTable, "_get_results", return_value=expected_results)
    instance = MockTestTable.from_mocks(query, input_data, query_template_kwargs)

    assert isinstance(instance, MockTestTable)
    assert isinstance(instance.SQLMockData.input_data, list)
    assert isinstance(instance.SQLMockData.rendered_query, str)
    assert isinstance(instance.SQLMockData.data, list)
    assert instance.SQLMockData.data == expected_results


# Test the _generate_input_data_cte_snippet method
def test_generate_input_data_cte_snippet(base_mock_table_instance):
    base_mock_table_instance.SQLMockData.input_data = [base_mock_table_instance]
    snippet = base_mock_table_instance._generate_input_data_cte_snippet()
    assert isinstance(snippet, str)
    assert "base_mock_table AS (" in snippet


# Test the _generate_query method
def test_generate_query():
    mock_table_instance = MockTestTable.from_dicts([])
    mock_table_instance.SQLMockData.input_data = [mock_table_instance]
    mock_table_instance.SQLMockData.rendered_query = "SELECT * FROM base_mock_table"
    query = mock_table_instance._generate_query()
    expected = dedent(
        f"""
    WITH {mock_table_instance.Meta.table_ref} AS (
    \tSELECT cast('1' AS Integer) AS col1, cast('hey' AS String) AS col2 WHERE FALSE
    ),

    result AS (
    \tSELECT * FROM base_mock_table
    )

    SELECT
    \tcast(col1 AS Integer) AS col1,
    \tcast(col2 AS String) AS col2
    FROM result
    """
    )

    assert expected == query
    assert isinstance(query, str)
    assert "WITH" in query
    assert "result AS (" in query


# Test the as_sql_input method
def test_as_sql_input():
    mock_table_instance = MockTestTable()
    mock_table_instance.SQLMockData.data = [
        {"col1": 1, "col2": "value1"},
        {"col1": 2, "col2": "value2"},
    ]
    sql_input = mock_table_instance.as_sql_input()
    expected = (
        f"{mock_table_instance.Meta.table_ref} AS (\n"
        "\tSELECT cast('1' AS Integer) AS col1, cast('value1' AS String) AS col2\n"
        "\tUNION ALL\n"
        "\tSELECT cast('2' AS Integer) AS col1, cast('value2' AS String) AS col2\n"
        ")"
    )
    assert expected == sql_input


# Test the assert_equal method
def test_assert_equal(base_mock_table_instance):
    expected_data = [{"column1": 1, "column2": "value1"}, {"column1": 2, "column2": "value2"}]
    base_mock_table_instance.SQLMockData.data = expected_data
    base_mock_table_instance.assert_equal(expected_data)


# Test the _to_sql_row method
def test_to_sql_row_all_values_provided():
    """...then the values should be used"""
    mock_data = [{"col1": 42, "col2": "test_value"}]
    mock_table = MockTestTable(data=mock_data)
    sql_row = mock_table._to_sql_row(mock_data[0])

    expected_sql_row = "cast('42' AS Integer) AS col1, cast('test_value' AS String) AS col2"
    assert sql_row == expected_sql_row


def test_to_sql_row_only_some_values_provided():
    """...then the missing values should be filled with the default"""
    mock_data = [{"col1": 42}]
    mock_table = MockTestTable(data=mock_data)
    sql_row = mock_table._to_sql_row(mock_data[0])

    expected_sql_row = "cast('42' AS Integer) AS col1, cast('hey' AS String) AS col2"
    assert sql_row == expected_sql_row


# Test the _to_sql_model method
def test_to_sql_model_no_data_provided():
    """...then it should populate a dummy row with defaults but filter for no results with WHERE FALSE"""
    mock_data = []
    mock_table = MockTestTable(mock_data)
    sql_model = mock_table.as_sql_input()

    expected_sql_model = (
        "mock_test_table AS (\n"
        "\tSELECT cast('1' AS Integer) AS col1, cast('hey' AS String) AS col2 WHERE FALSE\n"
        ")"
    )
    assert sql_model == expected_sql_model


def test_to_sql_model_single_row_provided():
    """...then it should only select data for that row and not add UNION ALL"""
    mock_data = [{"col1": 42, "col2": "test_value"}]
    mock_table = MockTestTable(mock_data)
    sql_model = mock_table.as_sql_input()

    expected_sql_model = (
        "mock_test_table AS (\n" "\tSELECT cast('42' AS Integer) AS col1, cast('test_value' AS String) AS col2\n" ")"
    )
    assert sql_model == expected_sql_model


def test_to_sql_model_multiple_provided():
    """...then it should combine the rows with UNION ALL"""
    mock_data = [{"col1": 42, "col2": "test_value"}, {"col1": 100, "col2": "another_value"}]
    mock_table = MockTestTable(mock_data)
    sql_model = mock_table.as_sql_input()

    expected_sql_model = (
        "mock_test_table AS (\n"
        "\tSELECT cast('42' AS Integer) AS col1, cast('test_value' AS String) AS col2\n"
        "\tUNION ALL\n"
        "\tSELECT cast('100' AS Integer) AS col1, cast('another_value' AS String) AS col2\n"
        ")"
    )
    assert sql_model == expected_sql_model


# Test assert_equal method
class TestData(BaseMockTable):
    name = StringTestColumn(default="Thomas")
    age = IntTestColumn(default=0)
    city = StringTestColumn(default="Munich")


def test_assert_equal_with_matching_data():
    # Arrange
    data_instance = TestData([{"name": "Alice", "age": 25}, {"name": "Bob", "age": 30}])
    expected_data = [{"name": "Alice", "age": 25}, {"name": "Bob", "age": 30}]

    # Act & Assert
    data_instance.assert_equal(expected_data)


def test_assert_equal_with_ignored_missing_keys():
    # Arrange
    data_instance = TestData(
        [{"name": "Alice", "age": 25, "city": "New York"}, {"name": "Bob", "age": 30, "city": "Munich"}]
    )
    expected_data = [{"name": "Alice", "age": 25}, {"name": "Bob", "age": 30}]

    # Act & Assert
    data_instance.assert_equal(expected_data, ignore_missing_keys=True)


def test_assert_equal_dict_ordering_differs_key_order_matches(base_mock_table_instance):
    expected_data = [{"column1": 1, "column2": "value1"}, {"column1": 2, "column2": "value2"}]
    base_mock_table_instance.SQLMockData.data = [
        {"column1": 2, "column2": "value2"},
        {"column1": 1, "column2": "value1"},
    ]
    base_mock_table_instance.assert_equal(expected_data)


def test_assert_equal_dict_ordering_differs_key_order_differs(base_mock_table_instance):
    expected_data = [{"column1": 1, "column2": "value1"}, {"column1": 2, "column2": "value2"}]
    base_mock_table_instance.SQLMockData.data = [
        {"column1": 2, "column2": "value2"},
        {"column2": "value1", "column1": 1},
    ]
    base_mock_table_instance.assert_equal(expected_data)


def test_assert_equal_with_non_matching_data():
    # Arrange
    data_instance = TestData([{"name": "Alice", "age": 25}, {"name": "Bob", "age": 30}])
    expected_data = [{"name": "Alice", "age": 30}, {"name": "Bob", "age": 25}]

    # Act & Assert
    with pytest.raises(AssertionError):
        data_instance.assert_equal(expected_data)


def test_assert_equal_with_ignored_missing_keys_and_non_matching_data():
    # Arrange
    data_instance = TestData([{"name": "Alice", "age": 25, "city": "New York"}, {"name": "Bob", "age": 30}])
    expected_data = [{"name": "Alice", "age": 30}]

    # Act & Assert
    with pytest.raises(AssertionError):
        data_instance.assert_equal(expected_data, ignore_missing_keys=True)


# Test validate input mocks function
def test_validate_input_mocks_no_table_ref_provided(mocker):
    """...then a validation error should be raised"""

    class NoTableRefMock(BaseMockTable):
        pass

    # Patch _get_results that we don't need to implement it
    mocker.patch.object(BaseMockTable, "_get_results", return_value=[])

    with pytest.raises(ValidationError):
        BaseMockTable.from_mocks(query="SELECT 1", input_data=[NoTableRefMock()])


def test_validate_input_mocks_with_table_ref_provided(mocker):
    """...then a validation error should be raised"""

    @table_meta(table_ref="some_table")
    class TableRefMock(BaseMockTable):
        def _get_results(self):
            return []

    # Patch _get_results that we don't need to implement it
    mocker.patch.object(BaseMockTable, "_get_results", return_value=[])

    # Should not raise an error
    BaseMockTable.from_mocks(query="SELECT 1", input_data=[TableRefMock()])
