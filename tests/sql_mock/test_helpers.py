# Test validate input mocks function
import pytest
import sqlglot

from sql_mock.column_mocks import BaseColumnMock
from sql_mock.exceptions import ValidationError
from sql_mock.helpers import (
    _validate_input_mocks_have_table_ref,
    _validate_unique_input_mocks,
    get_source_tables,
    replace_original_table_references,
    select_from_cte,
    validate_all_input_mocks_for_query_provided,
    validate_input_mocks,
)
from sql_mock.table_mocks import BaseTableMock, table_meta


class NoTableRefMock(BaseTableMock):
    pass


@table_meta(table_ref="some_table")
class TableRefMock(BaseTableMock):
    def _get_results(self):
        return []


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


class TestReplaceOriginalTableReference:
    def test_replace_original_table_references_when_reference_exists(self):
        """...then the original table reference should be replaced with the mocked table reference"""
        query_ast = sqlglot.parse_one(f"SELECT * FROM {MockTestTable._sql_mock_meta.table_ref}")
        # Note that sqlglot will add a comment with the original table name at the end
        expected = f"SELECT\n  *\nFROM {MockTestTable._sql_mock_meta.cte_name} /* data.mock_test_table */"
        assert expected == replace_original_table_references(
            query_ast=query_ast,
            table_ref=MockTestTable._sql_mock_meta.table_ref,
            sql_mock_cte_name=MockTestTable._sql_mock_meta.cte_name,
            dialect="bigquery",
        ).sql(pretty=True)

    def test_replace_original_table_references_when_reference_does_not_exist(self):
        """...then the original reference should not be replaced"""
        query_ast = sqlglot.parse_one("SELECT * FROM some_table")
        expected = "SELECT\n  *\nFROM some_table"
        assert expected == replace_original_table_references(
            query_ast=query_ast,
            table_ref=MockTestTable._sql_mock_meta.table_ref,
            sql_mock_cte_name=MockTestTable._sql_mock_meta.cte_name,
            dialect="bigquery",
        ).sql(pretty=True)

    def test_replace_original_table_reference_when_used_in_col_ref(self):
        """...then the column reference should also be replaced"""
        query = f"""
        SELECT {MockTestTable._sql_mock_meta.table_ref}.col1
        FROM data.some_table as b
        JOIN {MockTestTable._sql_mock_meta.table_ref} ON {MockTestTable._sql_mock_meta.table_ref}.col1 = b.col1
        """
        expected = f"SELECT\n  {MockTestTable._sql_mock_meta.cte_name}.col1\nFROM data.some_table AS b\nJOIN {MockTestTable._sql_mock_meta.cte_name} /* data.mock_test_table */\n  ON {MockTestTable._sql_mock_meta.cte_name}.col1 = b.col1"
        assert expected == replace_original_table_references(
            query_ast=sqlglot.parse_one(query),
            table_ref=MockTestTable._sql_mock_meta.table_ref,
            sql_mock_cte_name=MockTestTable._sql_mock_meta.cte_name,
            dialect="bigquery",
        ).sql(pretty=True)

    def test_replace_original_table_reference_when_used_in_col_ref_with_alias_that_has_same_name_as_table(self):
        """...then the alias should not be replaced"""
        query = f"""
        SELECT mock_test_table.col1
        FROM {MockTestTable._sql_mock_meta.table_ref} as mock_test_table
        JOIN data.some_table as a ON a.col1 = mock_test_table.col1
        """
        expected = f"SELECT\n  mock_test_table.col1\nFROM {MockTestTable._sql_mock_meta.cte_name} AS mock_test_table /* data.mock_test_table */\nJOIN data.some_table AS a\n  ON a.col1 = mock_test_table.col1"
        assert expected == replace_original_table_references(
            query_ast=sqlglot.parse_one(query),
            table_ref=MockTestTable._sql_mock_meta.table_ref,
            sql_mock_cte_name=MockTestTable._sql_mock_meta.cte_name,
            dialect="bigquery",
        ).sql(pretty=True)


class TestSelectFromCTE:
    def test_select_from_cte_when_cte_exists(self):
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

        assert expected == select_from_cte(query, cte_name, sql_dialect="bigquery")

    def test_select_from_cte_when_cte_does_not_exist(self):
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
            select_from_cte(query, cte_name, sql_dialect="bigquery")


class TestValidateUniqueInputMocks:
    def test_input_mocks_not_unique(self):
        """...then it should raise an error"""
        with pytest.raises(ValidationError):
            _validate_unique_input_mocks(input_mocks=[TableRefMock, TableRefMock])

    def test_input_mocks_unique(self):
        """...then it should NOT raise an error"""
        _validate_unique_input_mocks(input_mocks=[TableRefMock, NoTableRefMock])


class TestValidateInputMocksHaveTableRef:
    def test_validate_input_mocks_no_table_ref_provided(self):
        """...then a validation error should be raised"""
        with pytest.raises(ValidationError):
            _validate_input_mocks_have_table_ref(input_mocks=[NoTableRefMock()])

    def test_validate_input_mocks_with_table_ref_provided(self):
        """...then a validation error should be raised"""
        # Should not raise an error
        _validate_input_mocks_have_table_ref(input_mocks=[TableRefMock()])


def test_validate_input_mocks(mocker):
    mocked_unique_input_mocks_validation = mocker.patch("sql_mock.helpers._validate_unique_input_mocks")
    mocked_table_ref_validation = mocker.patch("sql_mock.helpers._validate_input_mocks_have_table_ref")
    input_mocks = [TableRefMock, NoTableRefMock]

    validate_input_mocks(input_mocks=input_mocks)

    mocked_unique_input_mocks_validation.assert_called_once_with(input_mocks)
    mocked_table_ref_validation.assert_called_once_with(input_mocks)


class TestValidateAllInputMocksForQueryProvided:
    query = """
    SELECT
        *
    FROM foo.foo AS f
    LEFT JOIN bar.bar AS b ON f.bar_id = b.id
    """

    @table_meta(table_ref="bar.bar")
    class BarMock(BaseTableMock):
        pass

    @table_meta(table_ref="foo.foo")
    class FooMock(BaseTableMock):
        pass

    def test_all_input_mocks_provided(self):
        """...then the validation should pass"""
        validate_all_input_mocks_for_query_provided(
            query=self.query, input_mocks=[self.BarMock, self.FooMock], dialect="bigquery"
        )

    def test_input_mocks_missing(self):
        """...then the validation should fail"""
        with pytest.raises(ValidationError) as e:
            validate_all_input_mocks_for_query_provided(
                query=self.query, input_mocks=[self.BarMock], dialect="bigquery"
            )
        assert str(e.value) == f"You need to provide the following input mocks to run your query: {['foo.foo']}"

    def test_input_mocks_not_in_query(self):
        """...then the validation should fail"""
        with pytest.raises(ValidationError) as e:
            validate_all_input_mocks_for_query_provided(
                query=self.query, input_mocks=[self.BarMock, self.FooMock, TableRefMock], dialect="bigquery"
            )
        assert (
            str(e.value)
            == f"Your input mock {TableRefMock.__class__.__name__} is not a table that is referenced in the query"
        )

    def test_input_mocks_missing_for_tables_within_mocked_cte(self):
        """...then the validation should pass since the CTE would be mocked anyways"""
        query = """
        WITH cte_1 AS (
            SELECT * FROM some_table
        ),

        cte_2 AS (
            SELECT a, b
            FROM cte_1
            WHERE a = 'foo'
        )

        SELECT a, b, * FROM cte_2
        """

        @table_meta(table_ref="cte_1")
        class Cte1Mock(BaseTableMock):
            pass

        validate_all_input_mocks_for_query_provided(query=query, input_mocks=[Cte1Mock()], dialect="bigquery")

    def test_cte_superfluous_after_mocking(self):
        """...then the validation should pass since the CTE will be removed anyways and does not need to be mocked"""
        query = """
        WITH cte_1 AS (
            SELECT * FROM some_table
        ),

        cte_2 AS (
            SELECT a, b
            FROM cte_1
            WHERE a = 'foo'
        )

        SELECT a, b, * FROM cte_2
        """

        @table_meta(table_ref="cte_2")  # This will make cte_1 superfluous
        class Cte1Mock(BaseTableMock):
            pass

        validate_all_input_mocks_for_query_provided(query=query, input_mocks=[Cte1Mock()], dialect="bigquery")


class TestGetSourceTables:
    def test_query_with_ctes(self):
        """...then only the real source table should be extracted"""
        query = """
        WITH foo AS (
            SELECT 1 FROM table_1
        )

        SELECT 2 FROM table_2
        """

        res = get_source_tables(query, dialect="bigquery")

        expected = ["table_1", "table_2"]
        assert len(res) == len(expected)
        assert all([val in expected for val in res])

    def test_query_with_multiple_references_of_single_table(self):
        """...then the tables should be unique"""

        query = """
        SELECT
            t1.1,
            t2.2
        FROM table_2 AS t1
        CROSS JOIN table_2 AS t2
        """

        res = get_source_tables(query, dialect="bigquery")

        expected = ["table_2"]
        assert len(res) == len(expected)
        assert all([val in expected for val in res])

    def test_query_with_comment(self):
        """...then the comment should be ignored"""

        query = """
        SELECT
            1,
            2
        FROM table_1 /* some comment */
        """

        res = get_source_tables(query, dialect="bigquery")

        expected = ["table_1"]
        assert res == expected

    def test_query_with_array_joins(self):
        """...then the array join fields should not be treated as tables to be mocked"""

        query = """
        SELECT
            sum(1) AS impressions,
            city,
            browser
        FROM
        (
            SELECT
                ['Istanbul', 'Berlin', 'Bobruisk'] AS cities,
                ['Firefox', 'Chrome', 'Chrome'] AS browsers
        )
        ARRAY JOIN
            cities AS city,
            browsers AS browser
        """

        res = get_source_tables(query, dialect="clickhouse")

        expected = []
        assert res == expected
