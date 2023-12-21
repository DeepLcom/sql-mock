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


@table_meta(table_ref="mock_test_table_with_defaults", default_inputs=[MockTestTable([])])
class MockTestTableWithDefaults(BaseMockTable):
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
    assert instance._sql_mock_data.columns == {"col1": int_col, "col2": string_col}
    assert instance._sql_mock_data.data == []


def test_wrong_fields_prodivded_to_model():
    """...then it should raise a validation error"""
    with pytest.raises(ValueError):
        MockTestTable(data=[{"not_existing_key": 1}])


# Test the from_mocks method
def test_from_mocks(base_mock_table_instance):
    query = "SELECT * FROM some_table"
    input_data = [base_mock_table_instance]
    query_template_kwargs = {}

    instance = MockTestTable.from_mocks(
        query=query, input_data=input_data, query_template_kwargs=query_template_kwargs
    )

    assert isinstance(instance, MockTestTable)
    assert instance._sql_mock_data.input_data == input_data
    assert instance._sql_mock_data.rendered_query == query
    assert instance._sql_mock_data.data == []


def test_from_mocks_with_defaults(base_mock_table_instance):
    query = "SELECT * FROM some_table"
    input_data = [*MockTestTableWithDefaults._sql_mock_data.default_inputs, base_mock_table_instance]
    query_template_kwargs = {}

    instance = MockTestTableWithDefaults.from_mocks(
        query=query, input_data=input_data, query_template_kwargs=query_template_kwargs
    )

    assert isinstance(instance, MockTestTableWithDefaults)
    assert instance._sql_mock_data.input_data == input_data
    assert instance._sql_mock_data.rendered_query == query
    assert instance._sql_mock_data.data == []


# Test the _generate_input_data_cte_snippet method
def test_generate_input_data_cte_snippet(base_mock_table_instance):
    base_mock_table_instance._sql_mock_data.input_data = [base_mock_table_instance]
    snippet = base_mock_table_instance._generate_input_data_cte_snippet()
    assert isinstance(snippet, str)
    assert "base_mock_table AS (" in snippet


# Test the as_sql_input method
def test_as_sql_input():
    mock_table_instance = MockTestTable()
    mock_table_instance._sql_mock_data.data = [
        {"col1": 1, "col2": "value1"},
        {"col1": 2, "col2": "value2"},
    ]
    sql_input = mock_table_instance.as_sql_input()
    expected = (
        f"{mock_table_instance._sql_mock_meta.table_ref} AS (\n"
        "\tSELECT cast('1' AS Integer) AS col1, cast('value1' AS String) AS col2\n"
        "\tUNION ALL\n"
        "\tSELECT cast('2' AS Integer) AS col1, cast('value2' AS String) AS col2\n"
        ")"
    )
    assert expected == sql_input


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
        "\tSELECT cast('1' AS Integer) AS col1, cast('hey' AS String) AS col2 FROM (SELECT 1) WHERE FALSE\n"
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
