from collections import Counter
from typing import TYPE_CHECKING, List

import sqlglot
from sqlglot.optimizer.eliminate_ctes import eliminate_ctes
from sqlglot.expressions import replace_tables
from sqlglot.optimizer.scope import build_scope

from sql_mock.exceptions import ValidationError

# Needed to avoid circular imports on type check
if TYPE_CHECKING:
    from sql_mock.table_mocks import BaseTableMock


def get_keys_from_list_of_dicts(data: list[dict]) -> set[str]:
    return set(key for dictionary in data for key in dictionary.keys())

def remove_cte_from_query(query_ast: sqlglot.Expression, cte_name: str) -> sqlglot.Expression:
    """
    Remove a CTE from a query

    Args:
        query_ast (sqlglot.Expression): The AST of the query
        cte_name (str): The name of the CTE to remove
    """
    for cte in query_ast.find_all(sqlglot.exp.CTE):
        if cte.alias == cte_name:
            cte.pop()
    return query_ast

def replace_original_table_references(query_ast: sqlglot.Expression, table_ref: str, sql_mock_cte_name: str, dialect: str) -> sqlglot.Expression:
    """
    Replace original table reference with sql mock cte name to point them to the mocked data

    Args:
        query_ast (str): Original SQL query - parsed by sqlglot
        table_ref (str): Table ref to be replaced
        sql_mock_cte_name (str): Name of the CTE that will contain the mocked data
        dialect (str): The SQL dialect to use for parsing the query
    """
    return replace_tables(expression=query_ast, mapping={table_ref: sql_mock_cte_name}, dialect=dialect)


def select_from_cte(query: str, cte_name: str, sql_dialect: str):
    """
    If selecting from a CTE, we need to replace the the final SELECT statement
    with a SELECT * FROM select_cte

    Args:
        query (str): Original SQL query
        cte_name (str): Name of the CTE to select from
        sql_dialect (str): The sql dialect to use for generating the query
    """
    ast = sqlglot.parse_one(query, dialect=sql_dialect)

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
    adjusted_query = ast.select("*").from_(cte_name).sql(pretty=True, dialect=sql_dialect)
    return adjusted_query


def parse_table_refs(table_ref, dialect):
    """Method to standardize how we parse table refs to avoid differences"""
    return table_ref if not table_ref else str(sqlglot.parse_one(table_ref, dialect=dialect))


def _clean_table_ref_transformer(node):
    node.comments = []
    node.set("alias", None)
    return node


def get_source_tables(query, dialect) -> List[str]:
    """
    Extract the unique tables that are references in FROM or JOIN statements.

    Based on https://github.com/tobymao/sqlglot/blob/9da41f22bdf5298dc94498173c338cdb16a2d36d/posts/ast_primer.md
    """
    ast = sqlglot.parse_one(query, dialect=dialect)
    root = build_scope(ast)

    tables = {
        str(source.transform(_clean_table_ref_transformer))
        # Traverse the Scope tree, not the AST
        for scope in root.traverse()
        # `selected_sources` contains sources that have been selected in this scope, e.g. in a FROM or JOIN clause.
        # `alias` is the name of this source in this particular scope.
        # `node` is the AST node instance
        # if the selected source is a subquery (including common table expressions),
        #     then `source` will be the Scope instance for that subquery.
        # if the selected source is a table,
        #     then `source` will be a Table instance.
        for alias, (node, source) in scope.selected_sources.items()
        if isinstance(source, sqlglot.exp.Table)
    }

    return list(tables)


def _validate_unique_input_mocks(input_mocks: List["BaseTableMock"]) -> None:
    counter = Counter(input_mocks)
    duplicated_mocks = [mock for mock, cnt in counter.items() if cnt > 1]
    if duplicated_mocks:
        msg = f"You provided multiple input mocks for: {duplicated_mocks}"
        raise ValidationError(msg)


def _validate_input_mocks_have_table_ref(input_mocks: List["BaseTableMock"]) -> None:
    missing_table_refs = [
        type(table_mock).__name__
        for table_mock in input_mocks
        if not getattr(table_mock._sql_mock_meta, "table_ref", False)
    ]

    if missing_table_refs:
        missing_table_ref_str = ",".join(missing_table_refs)
        msg = f"If you want to use a TableMock instance as input, you need to provide a table_reference using the table_meta decorator. Missing table refs for models: {missing_table_ref_str}"
        raise ValidationError(msg)


def validate_input_mocks(input_mocks: List["BaseTableMock"]):
    _validate_input_mocks_have_table_ref(input_mocks)
    _validate_unique_input_mocks(input_mocks)


def validate_all_input_mocks_for_query_provided(query: str, input_mocks: List["BaseTableMock"], dialect: str) -> None:
    """
    Validate that all input mocks are provided for a query.
    Mocks can replace CTEs or tables in the query. If a CTE is replaced, upstream table references don't need to be provided anymore.

    Args:
        query (str): The query to validate
        input_mocks (List[BaseTableMock]): The input mocks that are provided
        dialect (str): The SQL dialect to use for parsing the query
    """
    provided_table_refs = [table_mock._sql_mock_meta.table_ref for table_mock in input_mocks if hasattr(table_mock._sql_mock_meta, "table_ref")]
    ast = sqlglot.parse_one(query, dialect=dialect)

    # In case the table_ref is a CTE, we need to remove it from the query
    for table_ref in provided_table_refs:
        ast = remove_cte_from_query(query_ast=ast, cte_name=table_ref)

    # Now we might have some superfluous CTEs that are not referenced anymore
    remaining_query = eliminate_ctes(ast).sql(dialect=dialect, pretty=True)

    # The remaining query should not contain raw table references anymore if everything is mocked correctly
    missing_source_table_mocks = get_source_tables(query=remaining_query, dialect=dialect)
    for table_mock in input_mocks:
        table_ref = getattr(table_mock._sql_mock_meta, "table_ref", None)
        # If the table exists as mock, we can remove it from missing source tables
        try:
            missing_source_table_mocks.remove(table_ref)
        except ValueError:
            msg = f"Your input mock {table_mock.__class__.__name__} is not a table that is referenced in the query"
            raise ValidationError(msg)

    if missing_source_table_mocks:
        msg = f"You need to provide the following input mocks to run your query: {missing_source_table_mocks}"
        raise ValidationError(msg)
