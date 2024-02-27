import json
from sql_mock.constants import NO_INPUT, NoInput


class BaseColumnMock:
    """
    Represents a mock column in a database table.

    Attributes:
        dtype (str): The data type of the column.
        nullable: Indicator whether the column can be null
        default: The default value for the column.
        use_quotes_for_casting (bool): Indicator whether the value needs to be quoted (e.g. in the final cast)
    """

    dtype = None
    nullable = True
    default = None
    use_quotes_for_casting = True

    def __init__(self, default=None, nullable=True) -> None:
        """
        Initialize a BaseColumnMock instance.

        Args:
            default: The default value for the column.
            nullable (bool, optional): Whether the column is nullable. Default is False.
        """
        if default is None and not nullable:
            raise ValueError("Default cannot be None if column is not nullable")
        self.nullable = nullable
        self.default = default

    def to_sql(self, column_name: str, value=NO_INPUT) -> str:
        # Note: We compare against NO_INPUT instead of checking for None since None could be a valid input for nullable columns
        val = value if not isinstance(value, NoInput) else self.default
        # In case the val is None, we convert it to NULL
        if val is None:
            return f"cast(NULL AS {self.dtype}) AS {column_name}"

        # Check if the value is a list
        if isinstance(val, list):
            # Convert the list to a JSON string
            val = json.dumps(val)

        val = f"'{val}'" if self.use_quotes_for_casting else val
        return f"cast({val} AS {self.dtype}) AS {column_name}"

    def cast_field(self, column_name):
        return f"cast({column_name} AS {self.dtype}) AS {column_name}"
