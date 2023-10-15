import pytest

from sql_mock.column_mocks import ColumnMock
from sql_mock.table_mocks import BaseMockTable


class IntTestColumn(ColumnMock):
    dtype = "Integer"


class StringTestColumn(ColumnMock):
    dtype = "String"


int_col = IntTestColumn(default=1)
string_col = StringTestColumn(default="hey")


class MockTestTable(BaseMockTable):
    col1 = int_col
    col2 = string_col


# Create a fixture for an instance of BaseMockTable
@pytest.fixture
def base_mock_table_instance():
    return BaseMockTable()


# Test the __init__ method
def test_init():
    instance = MockTestTable()
    assert instance._columns == {"col1": int_col, "col2": string_col}
    assert instance._data == []


# Test the from_inputs method
def test_from_inputs(mocker):
    query = "SELECT * FROM some_table"
    input_data = {"some_table": base_mock_table_instance}
    query_template_kwargs = {}

    # Mock the _get_results method to return a simple list of dicts
    expected_results = [{"column1": 1, "column2": "value1"}, {"column1": 2, "column2": "value2"}]
    mocker.patch.object(BaseMockTable, "_get_results", return_value=expected_results)
    instance = BaseMockTable.from_inputs(query, input_data, query_template_kwargs)

    assert isinstance(instance, BaseMockTable)
    assert isinstance(instance._input_data, dict)
    assert isinstance(instance._rendered_query, str)
    assert isinstance(instance._data, list)
    assert instance._data == expected_results


# Test the _generate_input_data_cte_snippet method
def test_generate_input_data_cte_snippet(base_mock_table_instance):
    base_mock_table_instance._input_data = {"table1": base_mock_table_instance}
    snippet = base_mock_table_instance._generate_input_data_cte_snippet()
    assert isinstance(snippet, str)
    assert "table1 AS (" in snippet


# Test the _generate_query method
def test_generate_query(base_mock_table_instance):
    base_mock_table_instance._input_data = {"table1": base_mock_table_instance}
    base_mock_table_instance._rendered_query = "SELECT * FROM table1"
    query = base_mock_table_instance._generate_query()
    assert isinstance(query, str)
    assert "WITH" in query
    assert "result AS (" in query


# Test the as_sql_input method
def test_as_sql_input(base_mock_table_instance):
    base_mock_table_instance._data = [{"column1": 1, "column2": "value1"}, {"column1": 2, "column2": "value2"}]
    sql_input = base_mock_table_instance.as_sql_input()
    assert isinstance(sql_input, str)
    assert "SELECT" in sql_input
    assert "UNION ALL" in sql_input


# Test the assert_equal method
def test_assert_equal(base_mock_table_instance):
    expected_data = [{"column1": 1, "column2": "value1"}, {"column1": 2, "column2": "value2"}]
    base_mock_table_instance._data = expected_data
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

    expected_sql_model = "SELECT cast('1' AS Integer) AS col1, cast('hey' AS String) AS col2 WHERE FALSE"
    assert sql_model == expected_sql_model


def test_to_sql_model_single_row_provided():
    """...then it should only select data for that row and not add UNION ALL"""
    mock_data = [{"col1": 42, "col2": "test_value"}]
    mock_table = MockTestTable(mock_data)
    sql_model = mock_table.as_sql_input()

    expected_sql_model = "SELECT cast('42' AS Integer) AS col1, cast('test_value' AS String) AS col2"
    assert sql_model == expected_sql_model


def test_to_sql_model_multiple_provided():
    """...then it should combine the rows with UNION ALL"""
    mock_data = [{"col1": 42, "col2": "test_value"}, {"col1": 100, "col2": "another_value"}]
    mock_table = MockTestTable(mock_data)
    sql_model = mock_table.as_sql_input()

    expected_sql_model = (
        "SELECT cast('42' AS Integer) AS col1, cast('test_value' AS String) AS col2\n"
        "UNION ALL\n"
        "SELECT cast('100' AS Integer) AS col1, cast('another_value' AS String) AS col2"
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
