import json
import os
from typing import TYPE_CHECKING

import yaml

from sql_mock.config import SQLMockConfig
from sql_mock.helpers import parse_table_refs, validate_input_mocks
from sql_mock.table_mocks import TableMockMeta

# Needed to avoid circular imports on type check
if TYPE_CHECKING:
    from sql_mock.table_mocks import BaseTableMock


def _get_manifest_from_project_file(project_path: str) -> dict:
    with open(project_path, "r") as f:
        dbt_project = yaml.safe_load(f)
    target_path = dbt_project["target-path"]
    project_dir = os.path.dirname(project_path)
    with open(os.path.join(project_dir, target_path, "manifest.json"), "r") as file:
        manifest = json.load(file)
    return manifest


def _get_model_metadata(project_path: str, model_name: str) -> dict:
    """
    Extracts the rendered SQL query for a specified model from the dbt manifest file.

    Args:
        project_path (str): Path to the dbt_project.yml file.
        model_name (str): Name of the dbt model.

    Returns:
        dict: Dictionary of metadata from dbt (path to compiled sql query and table ref)
    """
    manifest = _get_manifest_from_project_file(project_path)
    project_dir = os.path.dirname(project_path)

    for node in manifest["nodes"].values():
        if node["resource_type"] == "model" and node["name"] == model_name:
            return {
                "query_path": os.path.join(project_dir, node["compiled_path"]),
                "table_ref": node["relation_name"],
            }

    raise ValueError(f"Model '{model_name}' not found in dbt manifest.")


def _get_source_metadata(project_path: str, source_name: str, table_name: str) -> dict:
    """
    Extracts the table metadata for dbt source from the manifest file.

    Args:
        project_path (str): Path to the dbt_project.yml file.
        source_name (str): Name of the dbt source.
        table_name (str): Name of the table in the dbt source.

    Returns:
        dict: Dictionary of metadata from dbt
    """
    manifest = _get_manifest_from_project_file(project_path)

    for node in manifest["sources"].values():
        if (
            node["resource_type"] == "source"
            and node["source_name"] == source_name
            and node["identifier"] == table_name
        ):
            return {
                "table_ref": node["relation_name"],
            }

    raise ValueError(f"Source '{source_name}' not found in dbt manifest.")


def _get_seed_metadata(project_path: str, seed_name: str) -> dict:
    """
    Extracts the table metadata for dbt seed from the manifest file.

    Args:
        project_path (str): Path to the dbt_project.yml file.
        seed_name (str): Name of the dbt seed.

    Returns:
        dict: Dictionary of metadata from dbt
    """
    manifest = _get_manifest_from_project_file(project_path)

    for node in manifest["nodes"].values():
        if node["resource_type"] == "seed" and node["name"] == seed_name:
            return {
                "table_ref": node["relation_name"],
            }

    raise ValueError(f"Seed '{seed_name}' not found in dbt manifest.")


def dbt_model_meta(model_name: str, project_path: str = None, default_inputs: ["BaseTableMock"] = None):
    """
    Decorator that is used to define TableMock metadata for dbt models.

    Args:
        model_name (string) : Name of the dbt model
        project_path (string): Path to the dbt manifest file
        default_inputs: List of default input mock instances that serve as default input if no other instance of that class is provided.
    """

    def decorator(cls):
        path = project_path or SQLMockConfig.get_dbt_project_path()

        dbt_meta = _get_model_metadata(project_path=path, model_name=model_name)

        parsed_query = ""
        with open(dbt_meta["query_path"]) as f:
            parsed_query = f.read()

        if default_inputs:
            validate_input_mocks(default_inputs)

        cls._sql_mock_meta = TableMockMeta(
            table_ref=parse_table_refs(dbt_meta["table_ref"], dialect=cls._sql_dialect),
            query=parsed_query,
            default_inputs=default_inputs or [],
        )
        return cls

    return decorator


def dbt_source_meta(
    source_name: str, table_name: str, project_path: str = None, default_inputs: ["BaseTableMock"] = None
):
    """
    Decorator that is used to define TableMock metadata for dbt sources.

    Args:
        source_name (string) : Name of source
        table_name (string): Name of the table in the source
        project_path (string): Path to the dbt manifest file
        default_inputs: List of default input mock instances that serve as default input if no other instance of that class is provided.
    """

    def decorator(cls):
        path = project_path or SQLMockConfig.get_dbt_project_path()

        dbt_meta = _get_source_metadata(
            project_path=path, source_name=source_name, table_name=table_name
        )

        if default_inputs:
            validate_input_mocks(default_inputs)

        cls._sql_mock_meta = TableMockMeta(
            table_ref=parse_table_refs(dbt_meta["table_ref"], dialect=cls._sql_dialect),
            default_inputs=default_inputs or [],
        )
        return cls

    return decorator


def dbt_seed_meta(seed_name: str, project_path: str = None, default_inputs: ["BaseTableMock"] = None):
    """
    Decorator that is used to define TableMock metadata for dbt sources.

    Args:
        seed_name (string) : Name of the dbt seed
        project_path (string): Path to the dbt manifest file
        default_inputs: List of default input mock instances that serve as default input if no other instance of that class is provided.
    """

    def decorator(cls):
        path = project_path or SQLMockConfig.get_dbt_project_path()

        dbt_meta = _get_seed_metadata(
            project_path=path,
            seed_name=seed_name,
        )

        if default_inputs:
            validate_input_mocks(default_inputs)

        cls._sql_mock_meta = TableMockMeta(
            table_ref=parse_table_refs(dbt_meta["table_ref"], dialect=cls._sql_dialect),
            default_inputs=default_inputs or [],
        )
        return cls

    return decorator
