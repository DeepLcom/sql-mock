from sql_mock.constants import NO_INPUT, NoInput


class ColumnMock:
    """
    Represents a mock column in a database table.

    Attributes:
        dtype (str): The data type of the column.
        nullable: Indicator whether the column can be null
        default: The default value for the column.
    """

    dtype = None
    nullable = False
    default = None

    def __init__(self, default=None, nullable=False) -> None:
        """
        Initialize a ColumnMock instance.

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
        return f"cast('{val}' AS {self.dtype}) AS {column_name}"

    def cast_field(self, column_name):
        return f"cast({column_name} AS {self.dtype}) AS {column_name}"
