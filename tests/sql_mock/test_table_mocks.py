import pytest

from sql_mock.column_mocks import BaseColumnMock
from sql_mock.table_mocks import BaseTableMock, TableMockMeta, table_meta


class IntTestColumn(BaseColumnMock):
    dtype = "Integer"


class StringTestColumn(BaseColumnMock):
    dtype = "String"


int_col = IntTestColumn(default=1)
string_col = StringTestColumn(default="hey")


@table_meta(table_ref="mock_test_table")
class MockTestTable(BaseTableMock):
    col1 = int_col
    col2 = string_col


@table_meta(table_ref="mock_test_table_with_defaults", default_inputs=[MockTestTable([])])
class MockTestTableWithDefaults(BaseTableMock):
    col1 = int_col
    col2 = string_col


# Create a fixture for an instance of BaseTableMock
@pytest.fixture
def base_table_mock_instance():
    @table_meta(table_ref="base_table_mock")
    class TableMock(BaseTableMock):
        pass

    return TableMock()


# Test the __init__ method
def test_init():
    instance = MockTestTable()
    assert instance._sql_mock_data.columns == {"col1": int_col, "col2": string_col}
    assert instance._sql_mock_data.data == []


def test_wrong_fields_prodivded_to_model():
    """...then it should raise a validation error"""
    with pytest.raises(ValueError):
        MockTestTable(data=[{"not_existing_key": 1}])


class TestFromMocks:
    def test_from_mocks(self, base_table_mock_instance, mocker):
        query = "SELECT * FROM some_table"
        input_data = [base_table_mock_instance]
        query_template_kwargs = {}
        mocked_validate_input_mocks_for_query = mocker.patch(
            "sql_mock.table_mocks.validate_all_input_mocks_for_query_provided"
        )
        mocked_validate_input_mocks = mocker.patch("sql_mock.table_mocks.validate_input_mocks")

        instance = MockTestTable.from_mocks(
            query=query, input_data=input_data, query_template_kwargs=query_template_kwargs
        )

        assert isinstance(instance, MockTestTable)
        assert instance._sql_mock_data.input_data == input_data
        assert instance._sql_mock_data.rendered_query == query
        assert instance._sql_mock_data.data == []
        mocked_validate_input_mocks_for_query.assert_called_once()
        mocked_validate_input_mocks.assert_called_once()

    def test_from_mocks_with_defaults(self, base_table_mock_instance, mocker):
        query = "SELECT * FROM some_table"
        input_data = [*MockTestTableWithDefaults._sql_mock_meta.default_inputs, base_table_mock_instance]
        query_template_kwargs = {}
        mocked_validate_input_mocks_for_query = mocker.patch(
            "sql_mock.table_mocks.validate_all_input_mocks_for_query_provided"
        )
        mocked_validate_input_mocks = mocker.patch("sql_mock.table_mocks.validate_input_mocks")

        instance = MockTestTableWithDefaults.from_mocks(
            query=query, input_data=input_data, query_template_kwargs=query_template_kwargs
        )

        assert isinstance(instance, MockTestTableWithDefaults)
        assert instance._sql_mock_data.input_data == input_data
        assert instance._sql_mock_data.rendered_query == query
        assert instance._sql_mock_data.data == []
        mocked_validate_input_mocks_for_query.assert_called_once()
        mocked_validate_input_mocks.assert_called_once()


# Test the _generate_input_data_cte_snippet method
def test_generate_input_data_cte_snippet(base_table_mock_instance):
    base_table_mock_instance._sql_mock_data.input_data = [base_table_mock_instance]
    snippet = base_table_mock_instance._generate_input_data_cte_snippet()
    assert isinstance(snippet, str)
    assert "base_table_mock AS (" in snippet


# Test the as_sql_input method
def test_as_sql_input():
    table_mock_instance = MockTestTable()
    table_mock_instance._sql_mock_data.data = [
        {"col1": 1, "col2": "value1"},
        {"col1": 2, "col2": "value2"},
    ]
    sql_input = table_mock_instance.as_sql_input()
    expected = (
        f"{table_mock_instance._sql_mock_meta.cte_name} AS (\n"
        "\tSELECT cast('1' AS Integer) AS col1, cast('value1' AS String) AS col2\n"
        "\tUNION ALL\n"
        "\tSELECT cast('2' AS Integer) AS col1, cast('value2' AS String) AS col2\n"
        ")"
    )
    assert expected == sql_input


class TestToSqlRow:
    def test_to_sql_row_all_values_provided(self):
        """...then the values should be used"""
        mock_data = [{"col1": 42, "col2": "test_value"}]
        table_mock = MockTestTable(data=mock_data)
        sql_row = table_mock._to_sql_row(mock_data[0])

        expected_sql_row = "cast('42' AS Integer) AS col1, cast('test_value' AS String) AS col2"
        assert sql_row == expected_sql_row

    def test_to_sql_row_only_some_values_provided(self):
        """...then the missing values should be filled with the default"""
        mock_data = [{"col1": 42}]
        table_mock = MockTestTable(data=mock_data)
        sql_row = table_mock._to_sql_row(mock_data[0])

        expected_sql_row = "cast('42' AS Integer) AS col1, cast('hey' AS String) AS col2"
        assert sql_row == expected_sql_row


class TestToSqlModel:
    def test_to_sql_model_no_data_provided(self):
        """...then it should populate a dummy row with defaults but filter for no results with WHERE FALSE"""
        mock_data = []
        table_mock = MockTestTable(mock_data)
        sql_model = table_mock.as_sql_input()

        expected_sql_model = (
            f"{table_mock._sql_mock_meta.cte_name} AS (\n"
            "\tSELECT cast('1' AS Integer) AS col1, cast('hey' AS String) AS col2 FROM (SELECT 1) WHERE FALSE\n"
            ")"
        )
        assert sql_model == expected_sql_model

    def test_to_sql_model_single_row_provided(self):
        """...then it should only select data for that row and not add UNION ALL"""
        mock_data = [{"col1": 42, "col2": "test_value"}]
        table_mock = MockTestTable(mock_data)
        sql_model = table_mock.as_sql_input()

        expected_sql_model = (
            f"{table_mock._sql_mock_meta.cte_name} AS (\n"
            "\tSELECT cast('42' AS Integer) AS col1, cast('test_value' AS String) AS col2\n"
            ")"
        )
        assert sql_model == expected_sql_model

    def test_to_sql_model_multiple_provided(self):
        """...then it should combine the rows with UNION ALL"""
        mock_data = [{"col1": 42, "col2": "test_value"}, {"col1": 100, "col2": "another_value"}]
        table_mock = MockTestTable(mock_data)
        sql_model = table_mock.as_sql_input()

        expected_sql_model = (
            f"{table_mock._sql_mock_meta.cte_name} AS (\n"
            "\tSELECT cast('42' AS Integer) AS col1, cast('test_value' AS String) AS col2\n"
            "\tUNION ALL\n"
            "\tSELECT cast('100' AS Integer) AS col1, cast('another_value' AS String) AS col2\n"
            ")"
        )
        assert sql_model == expected_sql_model


def test_cte_name():
    table_mock_meta = TableMockMeta(table_ref='"my-project.schema.table_name"')

    expected_cte_name = "sql_mock__my_project__schema__table_name"

    assert table_mock_meta.cte_name == expected_cte_name
