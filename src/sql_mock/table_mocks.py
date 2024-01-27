from textwrap import dedent, indent
from typing import List, Type

import sqlglot
from sqlglot.optimizer.eliminate_ctes import eliminate_ctes
from jinja2 import Template
from pydantic import BaseModel, ConfigDict, SkipValidation

from sql_mock.column_mocks import BaseColumnMock
from sql_mock.constants import NO_INPUT
from sql_mock.helpers import (
    get_keys_from_list_of_dicts,
    parse_table_refs,
    replace_original_table_references,
    remove_cte_from_query,
    select_from_cte,
    validate_all_input_mocks_for_query_provided,
    validate_input_mocks,
)


def table_meta(
    table_ref: str = "", query_path: str = None, query: str = None, default_inputs: ["BaseTableMock"] = None
):
    """
    Decorator that is used to define TableMock metadata

    Args:
        table_ref (string) : String that represents the table reference to the original table.
        query_path (string): Path to a SQL query file that should be used to generate the model. Can be a Jinja template. Note only one of query_path or query can be provided.
        query (string): Srting of the SQL query (can be in Jinja format). Note only one of query_path or query can be provided.
        default_inputs: List of default input mock instances that serve as default input if no other instance of that class is provided.
    """

    def decorator(cls):
        mock_meta_kwargs = {"table_ref": parse_table_refs(table_ref, dialect=cls._sql_dialect)}

        if query_path:
            with open(query_path) as f:
                mock_meta_kwargs["query"] = f.read()
        elif query:
            mock_meta_kwargs["query"] = query

        if default_inputs:
            validate_input_mocks(default_inputs)
            mock_meta_kwargs["default_inputs"] = default_inputs

        cls._sql_mock_meta = TableMockMeta(**mock_meta_kwargs)
        return cls

    return decorator


class SQLMockData(BaseModel):
    """
    Class to store data on BaseTableMock instances which is used during processing.
    We use this class to avoid collision with field names of the table we want to mock.
    """

    model_config = ConfigDict(arbitrary_types_allowed=True)

    columns: dict[str, Type[BaseColumnMock]] = None
    data: list[dict] = None
    input_data: list[dict] = None
    rendered_query: str = None
    last_query: str = None


class BaseTableMock:
    """
    Represents a base class for creating mock database tables for testing.
    When inheriting from this class you need to add column attributes for the table you would like to mock - e.g.:

    col1 = Int(default=1)

    Attributes:
        _sql_mock_data (SQLMockData): A class that stores data which is for processing. This is automatically created on instantiation.
        _sql_dialect (str): The sql dialect that the mock model uses. It will be leveraged by sqlglot.
    """

    _sql_mock_data: SQLMockData = None
    _sql_mock_meta: "TableMockMeta" = None
    _sql_dialect: str = None

    def __init__(self, data: list[dict] = None, sql_mock_data: SQLMockData = None) -> None:
        """
        Initialize a BaseTableMock instance.

        Args:
            data (list[dict]): A list of dictionaries representing rows of data.
        """
        # Create a data class instance to avoid collision with column names of the table we want to mock
        if sql_mock_data is not None:
            self._sql_mock_data = sql_mock_data
        # In case no decorator is used, the class does not yet have _sql_mock_data
        elif self._sql_mock_data is None:
            self._sql_mock_data = SQLMockData()

        self._sql_mock_data.columns = {
            field: getattr(self, field) for field in dir(self) if isinstance(getattr(self, field), BaseColumnMock)
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
        cls, input_data: list["BaseTableMock"] = None, query_template_kwargs: dict = None, query: str = None
    ):
        """
        Instantiate the mock table from input mocks. This runs the tables query with static data provided by the input mocks.

        Arguments:
            input_data: List of TableMock instances that hold static data that should be used as inputs.
            query_template_kwargs: Dictionary of Jinja template key-value pairs that should be used to render the query.
            query: String of the SQL query that is used to generate the model. Can be a Jinja template. If provided, it overwrites the query on cls._sql_mock_meta.query.
        """
        instance = cls(data=[])
        query_template = Template(query or cls._sql_mock_meta.query)
        query = query_template.render(query_template_kwargs or {})
        instance._sql_mock_data.rendered_query = query

        # Update defaults with provided data. We use the table ref dictionaries to avoid duplicated inputs.
        if getattr(cls._sql_mock_meta, "default_inputs", None):
            default_inputs = {
                table_mock._sql_mock_meta.table_ref: table_mock for table_mock in cls._sql_mock_meta.default_inputs
            }
            input_dict = {table_mock._sql_mock_meta.table_ref: table_mock for table_mock in input_data}
            input_data = list({**default_inputs, **input_dict}.values())

        validate_input_mocks(input_data)
        validate_all_input_mocks_for_query_provided(query=query, dialect=cls._sql_dialect, input_mocks=input_data)
        instance._sql_mock_data.input_data = input_data

        return instance

    def _generate_input_data_cte_snippet(self):
        # Convert instances into SQL snippets that serve as input to a CTE
        table_ctes = [table_mock.as_sql_input() for table_mock in self._sql_mock_data.input_data]
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

        # Parse the query with sqlglot to to standardize it (e.g. removes semi-colons)
        result_query = sqlglot.parse_one(self._sql_mock_data.rendered_query, dialect=self._sql_dialect).sql(
            dialect=self._sql_dialect
        )

        if cte_to_select is not None:
            result_query = select_from_cte(result_query, cte_to_select, sql_dialect=self._sql_dialect)
            final_columns_to_select = "*"
        else:
            final_columns_to_select = ",\n".join(
                [col.cast_field(column_name=column_name) for column_name, col in self._sql_mock_data.columns.items()]
            )

        query = query_template.format(
            input_data_ctes=input_data_ctes,
            result_query=result_query,
            final_columns_to_select=final_columns_to_select,
        )

        query_ast = sqlglot.parse_one(query, dialect=self._sql_dialect)
        for table_mock in self._sql_mock_data.input_data:
            query_ast = table_mock.replace_original_references(query_ast=query_ast)

        # Remove superfluous CTEs
        query_ast = eliminate_ctes(query_ast)
        query = query_ast.sql(pretty=True, dialect=self._sql_dialect)
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
            snippet += " FROM (SELECT 1) WHERE FALSE"
        else:
            snippet = "\nUNION ALL\nSELECT ".join(
                [self._to_sql_row(row_data) for row_data in self._sql_mock_data.data]
            )

        # Indent whole CTE content for better query readability
        snippet = indent(f"SELECT {snippet}", "\t")
        return f"{self._sql_mock_meta.cte_name} AS (\n{snippet}\n)"

    def replace_original_references(self, query_ast: sqlglot.Expression) -> sqlglot.Expression:
        # In case we mock a CTE, we need to drop the original CTE from the query
        query_ast = remove_cte_from_query(query_ast=query_ast, cte_name=self._sql_mock_meta.table_ref)

        return replace_original_table_references(
            query_ast=query_ast,
            table_ref=self._sql_mock_meta.table_ref,
            sql_mock_cte_name=self._sql_mock_meta.cte_name,
            dialect=self._sql_dialect,
        )

    def _assert_equal(
        self,
        data: [dict],
        expected: [dict],
        ignore_missing_keys: bool = False,
        ignore_order: bool = True,
        print_query_on_fail: bool = True,
    ):
        """
        Assert that the provided data matches the expected data.

        Args:
            data (list of dicts): Actual result data to compare the class data against
            expected (list of dicts): Expected data to compare the class data against
            ignore_missing_keys (bool): If true, the comparison will only happen for the fields that are present in the
                list of dictionaries of the `expected` argument.
            ignore_order (bool): If true, the order of dicts / rows will be ignored for comparison.
            print_query_on_fai (bool)l: If true, the tested query will be printed to the console output when the test fails.
        """
        if ignore_missing_keys:
            keys_to_keep = get_keys_from_list_of_dicts(expected)
            data = [{key: value for key, value in dictionary.items() if key in keys_to_keep} for dictionary in data]
        if ignore_order:
            def sort_handling_none(d):
                """
                Sorts a dictionary by its values, but handles None values as -inf.
                We do this to avoid issues with mixed None and non-None values in the same column.
                """
                none_safe_items = [(key, value) if value is not None else (key, float('-inf')) for key, value in d.items()]
                return sorted(none_safe_items)
            data = sorted(data, key=sort_handling_none)
            expected = sorted(expected, key=sort_handling_none)
        try:
            assert expected == data
        except Exception as e:
            if print_query_on_fail:
                print(self._sql_mock_data.last_query)
            raise e

    def assert_cte_equal(
        self,
        cte_name,
        expected: [dict],
        ignore_missing_keys: bool = False,
        ignore_order: bool = True,
        print_query_on_fail: bool = True,
    ):
        """
        Assert that a CTE within the table mock's query equals the provided expected data.

        Args:
            cte_name (str): Name of the CTE that should be compared against the expected results
            expected (list of dicts): Expected data to compare the class data against
            ignore_missing_keys (bool): If true, the comparison will only happen for the fields that are present in the
                list of dictionaries of the `expected` argument.
            ignore_order (bool): If true, the order of dicts / rows will be ignored for comparison.
            print_query_on_fail (bool): If true, the tested query will be printed to the console output when the test fails.
        """
        query = self._generate_query(cte_to_select=cte_name)
        data = self._get_results(query)
        self._assert_equal(
            data=data,
            expected=expected,
            ignore_missing_keys=ignore_missing_keys,
            ignore_order=ignore_order,
            print_query_on_fail=print_query_on_fail,
        )

    def assert_equal(
        self,
        expected: [dict],
        ignore_missing_keys: bool = False,
        ignore_order: bool = True,
        print_query_on_fail: bool = True,
    ):
        """
        Assert that the result of the table mock's query equals the provided expected data.

        Args:
            expected (list of dicts): Expected data to compare the class data against
            ignore_missing_keys (bool): If true, the comparison will only happen for the fields that are present in the
                list of dictionaries of the `expected` argument.
            ignore_order (bool): If true, the order of dicts / rows will be ignored for comparison.
            print_query_on_fail (bool): If true, the tested query will be printed to the console output when the test fails.
        """
        query = self._generate_query()
        data = self._get_results(query)
        self._assert_equal(
            data=data,
            expected=expected,
            ignore_missing_keys=ignore_missing_keys,
            ignore_order=ignore_order,
            print_query_on_fail=print_query_on_fail,
        )


class TableMockMeta(BaseModel):
    """
    Class to store static metadata of BaseTableMock instances which is used during processing.
    We use this class to avoid collision with field names of the table we want to mock.

    Attributes:
        table_ref (string) : String that represents the table reference to the original table.
        query (string): Srting of the SQL query (can be in Jinja format).
    """

    model_config = ConfigDict(arbitrary_types_allowed=True)

    default_inputs: List[SkipValidation["BaseTableMock"]] = None
    table_ref: str = None
    query: str = None

    @property
    def cte_name(self):
        if getattr(self, "table_ref", None):
            cleaned_ref = self.table_ref.replace('"', "").replace(".", "__").replace("-", "_")
            return f"sql_mock__{cleaned_ref}"
