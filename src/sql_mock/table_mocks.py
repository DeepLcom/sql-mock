from jinja2 import Template

from sql_mock.column_mocks import ColumnMock
from sql_mock.constants import NO_INPUT
from sql_mock.exceptions import ValidationError


def get_keys_from_list_of_dicts(data: list[dict]) -> set[str]:
    return set(key for dictionary in data for key in dictionary.keys())


def table_meta(table_ref):
    """Decorator that is used to define MockTable metadata"""

    def decorator(cls):
        cls._table_ref = table_ref
        return cls

    return decorator


def validate_input_mocks(table_mocks: list["BaseMockTable"]):
    # Check that each input table mock has a _table_ref defined
    missing_table_refs = [type(mock_table).__name__ for mock_table in table_mocks if not mock_table._table_ref]
    if missing_table_refs:
        missing_table_ref_str = ",".join(missing_table_refs)
        msg = f"If you want to use a MockTable instance as input, you need to provide a table_reference using the table_meta decorator. Missing table refs for models: {missing_table_ref_str}"
        raise ValidationError(msg)


class BaseMockTable:
    """
    Represents a base class for creating mock database tables for testing.
    When inheriting from this class you need to add column attributes for the table you would like to mock - e.g.:

    col1 = Int(default=1)

    Attributes:
        _table_ref (string) : String that represents the table reference to the original table.
        _columns (dict): An auto-generated dictionary of column names and corresponding ColumnMock instances.
        _data (list): An auto-generated list of dictionaries representing rows of data.
        _input_data (list): An auto-generated list of dictonaries representing the upstream model input data
        _rendered_query (string): The fully rendered query based on jinja keyword arguments provided
    """

    # Metadata that needs to be provided by the table_meta decorator
    _table_ref = None

    # Auto generated
    _columns = None
    _data = None
    _input_data = None
    _rendered_query = None

    def __init__(self, data: list[dict] = None) -> None:
        """
        Initialize a BaseMockTable instance.

        Args:
            data (list[dict]): A list of dictionaries representing rows of data.
        """
        self._columns = {
            field: getattr(self, field) for field in dir(self) if isinstance(getattr(self, field), ColumnMock)
        }

        if data is not None:
            provided_keys = get_keys_from_list_of_dicts(data)
            not_existing_fields = [key for key in provided_keys if key not in self._columns.keys()]
            if not_existing_fields:
                raise ValueError(
                    f"Fields provided that are not part of the table's fields. Non existing fields: {not_existing_fields}"
                )

        self._data = [] if data is None else data

    @classmethod
    def from_dicts(cls, data: list[dict] = None):
        return cls(data=data)

    @classmethod
    def from_mocks(cls, query, input_data: list["BaseMockTable"] = None, query_template_kwargs: dict = None):
        validate_input_mocks(input_data)

        instance = cls(data=[])
        query_template = Template(query)

        # Assign instance attributes
        instance._input_data = input_data
        instance._rendered_query = query_template.render(query_template_kwargs or {})

        instance._data = instance._get_results()

        return instance

    def _generate_input_data_cte_snippet(self):
        # Convert instances into SQL snippets that serve as input to a CTE
        table_ctes = [mock_table.as_sql_input() for mock_table in self._input_data]
        return ",\n".join(table_ctes)

    def _generate_query(
        self,
    ):
        query_template = """
        WITH {input_data_ctes},

        result AS (
        {result_query}
        )

        SELECT
            {casted_result_fields}
        FROM result
        """
        input_data_ctes = self._generate_input_data_cte_snippet()
        casted_result_fields = ",\n".join(
            [col.cast_field(column_name=column_name) for column_name, col in self._columns.items()]
        )

        query = query_template.format(
            input_data_ctes=input_data_ctes,
            result_query=self._rendered_query,
            casted_result_fields=casted_result_fields,
        )

        # Replace orignal table references to point them to the mocked data
        for mock_table in self._input_data:
            new_reference = mock_table._table_ref.replace(".", "__")
            query = query.replace(mock_table._table_ref, new_reference)

        # Store last query for debugging
        self._last_query = query
        return query

    def _get_results(self) -> list[dict]:
        """
        This method needs to be implemented for database specific Table Mocks
        """
        # This is how you can get the fully rendered test query:
        # query = self._generate_query()
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
                for column_name, col in self._columns.items()
            ]
        )

    def as_sql_input(self):
        """
        Generate a UNION ALL SQL CTE that combines data from all rows.

        Returns:
            str: A SQL query that combines data from all rows.
        """
        # Convert the instance into a SQL snippet for CTE input
        if len(self._data) == 0:
            # Populate default values row with a WHERE FALSE statement to simulate no rows for the model
            snippet = self._to_sql_row({})
            snippet += " WHERE FALSE"
        else:
            snippet = "\nUNION ALL\nSELECT ".join([self._to_sql_row(row_data) for row_data in self._data])
        return f"{self._table_ref} AS (\n" f"SELECT {snippet}\n" ")"

    def assert_equal(self, expected: [dict], ignore_missing_keys: bool = False, ignore_order: bool = True):
        """
        Assert that the class data matches the expected data.

        This is a helper function that can be used for tests.

        Args:
            expected (list of dicts): Expected data to compare the class data against
            ignore_missing_keys (bool): If true, the comparison will only happen for the fields that are present in the
                list of dictionaries of the `expected` argument.
            ignore_order (bool): If true, the order of dicts / rows will be ignored for comparison.
        """
        data = self._data
        if ignore_missing_keys:
            keys_to_keep = get_keys_from_list_of_dicts(expected)
            data = [{key: value for key, value in dictionary.items() if key in keys_to_keep} for dictionary in data]
        if ignore_order:
            data = sorted(data, key=lambda d: sorted(d.items()))
            expected = sorted(expected, key=lambda d: sorted(d.items()))
        assert expected == data
