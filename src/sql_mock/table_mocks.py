from textwrap import dedent, indent
from typing import Type

import sqlglot
from jinja2 import Template
from pydantic import BaseModel

from sql_mock.column_mocks import ColumnMock
from sql_mock.constants import NO_INPUT
from sql_mock.exceptions import ValidationError


def get_keys_from_list_of_dicts(data: list[dict]) -> set[str]:
    return set(key for dictionary in data for key in dictionary.keys())


def replace_original_table_references(query: str, mock_tables: list["BaseMockTable"]):
    """
    Replace orignal table references to point them to the mocked data

    Args:
        query (str): Original SQL query
        mock_tables (list[BaseMockTable]): List of BaseMockTable instances that are used as input
    """
    for mock_table in mock_tables:
        new_reference = mock_table._sql_mock_meta.table_ref.replace(".", "__")
        query = query.replace(mock_table._sql_mock_meta.table_ref, new_reference)
    return query


def select_from_cte(query: str, cte_name: str):
    """
    If selecting from a CTE, we need to replace the the final SELECT statement
    with a SELECT * FROM select_cte

    Args:
        query (str): Original SQL query
        cte_name (str): Name of the CTE to select from
    """
    ast = sqlglot.parse_one(query)

    # Check whether the cte exists, if not raise an error
    cte_exists = any(cte.alias == cte_name for cte in ast.find_all(sqlglot.exp.CTE))
    if not cte_exists:
        raise ValueError(f"CTE with name {cte_name} does not exist in query")

    root_select_statement = ast.find(sqlglot.exp.Select)
    # Remove all columns from root select statement
    for col in root_select_statement.find_all((sqlglot.exp.Column, sqlglot.exp.Star)):
        # Only drop columns from the root select statement
        if col.parent == root_select_statement:
            col.pop()

    # Change the final select statement to SELECT * FROM <cte_name>
    adjusted_query = ast.select("*").from_(cte_name).sql(pretty=True)
    return adjusted_query


class MockTableMeta(BaseModel):
    """
    Class to store metadata of BaseMockTable instances which is used during processing.
    We use this class to avoid collision with field names of the table we want to mock.

    Attributes:
        table_ref (string) : String that represents the table reference to the original table.
        query (string): Srting of the SQL query (can be in Jinja format).
    """

    table_ref: str = None
    query: str = None


def table_meta(table_ref: str = "", query_path: str = None, query: str = None):
    """
    Decorator that is used to define MockTable metadata

    Args:
        table_ref (string) : String that represents the table reference to the original table.
        query_path (string): Path to a SQL query file that should be used to generate the model. Can be a Jinja template. Note only one of query_path or query can be provided.
        query (string): Srting of the SQL query (can be in Jinja format). Note only one of query_path or query can be provided.
    """

    def decorator(cls):
        mock_meta_kwargs = {"table_ref": table_ref}

        if query_path:
            with open(query_path) as f:
                mock_meta_kwargs["query"] = f.read()
        elif query:
            mock_meta_kwargs["query"] = query

        cls._sql_mock_meta = MockTableMeta(**mock_meta_kwargs)
        return cls

    return decorator


def validate_input_mocks(table_mocks: list["BaseMockTable"]):
    # Check that each input table mock has a _table_ref defined
    missing_table_refs = [
        type(mock_table).__name__
        for mock_table in table_mocks
        if not getattr(mock_table._sql_mock_meta, "table_ref", False)
    ]
    if missing_table_refs:
        missing_table_ref_str = ",".join(missing_table_refs)
        msg = f"If you want to use a MockTable instance as input, you need to provide a table_reference using the table_meta decorator. Missing table refs for models: {missing_table_ref_str}"
        raise ValidationError(msg)


class SQLMockData(BaseModel):
    """
    Class to store data on BaseMockTable instances which is used during processing.
    We use this class to avoid collision with field names of the table we want to mock.
    """

    columns: dict[str, Type[ColumnMock]] = None
    data: list[dict] = None
    input_data: list[dict] = None
    rendered_query: str = None
    last_query: str = None


class BaseMockTable:
    """
    Represents a base class for creating mock database tables for testing.
    When inheriting from this class you need to add column attributes for the table you would like to mock - e.g.:

    col1 = Int(default=1)

    Attributes:
        _sql_mock_data (SQLMockData): A class that stores data which is for processing. This is automatcially created on instantiation.
        _sql_mock_meta (MockTableMeta): A class attribute to store table metadata. It is created using the `table_meta` decorator.
    """

    _sql_mock_meta: MockTableMeta = None
    _sql_mock_data: SQLMockData = None

    def __init__(self, data: list[dict] = None) -> None:
        """
        Initialize a BaseMockTable instance.

        Args:
            data (list[dict]): A list of dictionaries representing rows of data.
        """
        # Create a data class instance to avoid collision with column names of the table we want to mock
        self._sql_mock_data = SQLMockData()

        self._sql_mock_data.columns = {
            field: getattr(self, field) for field in dir(self) if isinstance(getattr(self, field), ColumnMock)
        }

        if data is not None:
            provided_keys = get_keys_from_list_of_dicts(data)
            not_existing_fields = [key for key in provided_keys if key not in self._sql_mock_data.columns.keys()]
            if not_existing_fields:
                raise ValueError(
                    f"Fields provided that are not part of the table's fields. Non existing fields: {not_existing_fields}"
                )

        self._sql_mock_data.data = [] if data is None else data

    @classmethod
    def from_dicts(cls, data: list[dict] = None):
        return cls(data=data)

    @classmethod
    def from_mocks(
        cls, input_data: list["BaseMockTable"] = None, query_template_kwargs: dict = None, query: str = None
    ):
        """
        Instantiate the mock table from input mocks. This runs the tables query with static data provided by the input mocks.

        Arguments:
            input_data: List of MockTable instances that hold static data that should be used as inputs.
            query_template_kwargs: Dictionary of Jinja template key-value pairs that should be used to render the query.
            query: String of the SQL query that is used to generate the model. Can be a Jinja template. If provided, it overwrites the query on cls._sql_mock_meta.query.
        """
        validate_input_mocks(input_data)

        instance = cls(data=[])
        query_template = Template(query or cls._sql_mock_meta.query)

        # Assign instance attributes
        instance._sql_mock_data.input_data = input_data
        instance._sql_mock_data.rendered_query = query_template.render(query_template_kwargs or {})

        return instance

    def _generate_input_data_cte_snippet(self):
        # Convert instances into SQL snippets that serve as input to a CTE
        table_ctes = [mock_table.as_sql_input() for mock_table in self._sql_mock_data.input_data]
        return ",\n".join(table_ctes)

    def _generate_query(
        self,
        cte_to_select: str = None,
    ):
        query_template = dedent(
            """
        WITH {input_data_ctes},

        result AS (
        {result_query}
        )

        SELECT
        {final_columns_to_select}
        FROM result
        """
        )
        input_data_ctes = self._generate_input_data_cte_snippet()
        result_query = self._sql_mock_data.rendered_query

        if cte_to_select is not None:
            result_query = select_from_cte(result_query, cte_to_select)
            final_columns_to_select = "*"
        else:
            final_columns_to_select = ",\n".join(
                [col.cast_field(column_name=column_name) for column_name, col in self._sql_mock_data.columns.items()]
            )

        query = query_template.format(
            input_data_ctes=input_data_ctes,
            result_query=indent(result_query, "\t"),
            final_columns_to_select=indent(final_columns_to_select, "\t"),
        )

        query = replace_original_table_references(query, mock_tables=self._sql_mock_data.input_data)
        # Store last query for debugging
        self._sql_mock_data.last_query = query
        return query

    def _get_results(self, query: str) -> list[dict]:
        """
        This method needs to be implemented for database specific Table Mocks
        """
        raise NotImplementedError("Child classes need to implement this method")

    def _to_sql_row(self, row_data: dict) -> str:
        """
        Convert a dictionary of column-value pairs into a SQL row string.

        Args:
            row_data (dict): Dictionary containing the column-value pairs for the row.

        Returns:
            str: A SQL row string.
        """
        return ", ".join(
            [
                col.to_sql(column_name=column_name, value=row_data.get(column_name, NO_INPUT))
                for column_name, col in self._sql_mock_data.columns.items()
            ]
        )

    def as_sql_input(self):
        """
        Generate a UNION ALL SQL CTE that combines data from all rows.

        Returns:
            str: A SQL query that combines data from all rows.
        """
        # Convert the instance into a SQL snippet for CTE input
        if len(self._sql_mock_data.data) == 0:
            # Populate default values row with a WHERE FALSE statement to simulate no rows for the model
            snippet = self._to_sql_row({})
            snippet += " WHERE FALSE"
        else:
            snippet = "\nUNION ALL\nSELECT ".join(
                [self._to_sql_row(row_data) for row_data in self._sql_mock_data.data]
            )

        # Indent whole CTE content for better query readability
        snippet = indent(f"SELECT {snippet}", "\t")
        return f"{self._sql_mock_meta.table_ref} AS (\n{snippet}\n)"

    def _assert_equal(
        self, data: [dict], expected: [dict], ignore_missing_keys: bool = False, ignore_order: bool = True
    ):
        """
        Assert that the provided data matches the expected data.

        Args:
            data (list of dicts): Actual result data to compare the class data against
            expected (list of dicts): Expected data to compare the class data against
            ignore_missing_keys (bool): If true, the comparison will only happen for the fields that are present in the
                list of dictionaries of the `expected` argument.
            ignore_order (bool): If true, the order of dicts / rows will be ignored for comparison.
        """
        if ignore_missing_keys:
            keys_to_keep = get_keys_from_list_of_dicts(expected)
            data = [{key: value for key, value in dictionary.items() if key in keys_to_keep} for dictionary in data]
        if ignore_order:
            data = sorted(data, key=lambda d: sorted(d.items()))
            expected = sorted(expected, key=lambda d: sorted(d.items()))
        assert expected == data

    def assert_cte_equal(
        self, cte_name, expected: [dict], ignore_missing_keys: bool = False, ignore_order: bool = True
    ):
        """
        Assert that a CTE within the table mock's query equals the provided expected data.

        Args:
            cte_name (str): Name of the CTE that should be compared against the expected results
            expected (list of dicts): Expected data to compare the class data against
            ignore_missing_keys (bool): If true, the comparison will only happen for the fields that are present in the
                list of dictionaries of the `expected` argument.
            ignore_order (bool): If true, the order of dicts / rows will be ignored for comparison.
        """
        query = self._generate_query(cte_to_select=cte_name)
        data = self._get_results(query)
        self._assert_equal(
            data=data, expected=expected, ignore_missing_keys=ignore_missing_keys, ignore_order=ignore_order
        )

    def assert_equal(self, expected: [dict], ignore_missing_keys: bool = False, ignore_order: bool = True):
        """
        Assert that the result of the table mock's query equals the provided expected data.

        Args:
            expected (list of dicts): Expected data to compare the class data against
            ignore_missing_keys (bool): If true, the comparison will only happen for the fields that are present in the
                list of dictionaries of the `expected` argument.
            ignore_order (bool): If true, the order of dicts / rows will be ignored for comparison.
        """
        query = self._generate_query()
        data = self._get_results(query)
        self._assert_equal(
            data=data, expected=expected, ignore_missing_keys=ignore_missing_keys, ignore_order=ignore_order
        )
