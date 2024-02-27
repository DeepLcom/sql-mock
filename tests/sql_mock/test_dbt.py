import pytest

from sql_mock.config import SQLMockConfig
from sql_mock.dbt import (
    _get_model_metadata,
    _get_seed_metadata,
    _get_source_metadata,
    dbt_model_meta,
    dbt_seed_meta,
    dbt_source_meta,
)
from sql_mock.table_mocks import BaseTableMock


class TestDbtModelMeta:
    def test_project_path_provided(self, mocker):
        """...then metadata should be extracted from that project path"""
        project_path = "path/to/my/project"

        # We set another path in the config but it should be overwritten
        SQLMockConfig.set_dbt_project_path("some/other/path")

        model_name = "my_model"
        returned_query_path = "some/path/to/query.sql"
        returned_table_ref = "db.my_model"

        mocked_get_model_metadata = mocker.patch(
            "sql_mock.dbt._get_model_metadata"
        )
        mocked_get_model_metadata.return_value = {
            "query_path": returned_query_path,
            "table_ref": returned_table_ref,
        }

        query = "SELECT bar FROM foo"
        mock_open = mocker.patch("builtins.open")
        # Configure the mock to return the file content
        mock_open.return_value.__enter__.return_value.read.return_value = query

        @dbt_model_meta(model_name=model_name, project_path=project_path)
        class TestMock(BaseTableMock):
            pass

        assert TestMock._sql_mock_meta.query == query
        assert TestMock._sql_mock_meta.table_ref == returned_table_ref
        mock_open.assert_called_once_with(returned_query_path)
        mocked_get_model_metadata.assert_called_once_with(
            project_path=project_path, model_name=model_name
        )

    def test_project_path_not_provided_but_set_in_config(self, mocker):
        """...then metadata should be extracted from the project path provided in the config"""
        project_path = "path/to/my/project"
        SQLMockConfig.set_dbt_project_path(project_path)

        model_name = "my_model"
        returned_query_path = "some/path/to/query.sql"
        returned_table_ref = "db.my_model"

        mocked_get_model_metadata = mocker.patch(
            "sql_mock.dbt._get_model_metadata"
        )
        mocked_get_model_metadata.return_value = {
            "query_path": returned_query_path,
            "table_ref": returned_table_ref,
        }

        query = "SELECT bar FROM foo"
        mock_open = mocker.patch("builtins.open")
        # Configure the mock to return the file content
        mock_open.return_value.__enter__.return_value.read.return_value = query

        @dbt_model_meta(model_name=model_name)
        class TestMock(BaseTableMock):
            pass

        assert TestMock._sql_mock_meta.query == query
        assert TestMock._sql_mock_meta.table_ref == returned_table_ref
        mock_open.assert_called_once_with(returned_query_path)
        mocked_get_model_metadata.assert_called_once_with(
            project_path=project_path, model_name=model_name
        )


class TestDbtSourceMeta:
    def test_project_path_provided(self, mocker):
        """...then metadata should be extracted from that project path"""
        project_path = "path/to/my/project"

        # We set another path in the config but it should be overwritten
        SQLMockConfig.set_dbt_project_path("some/other/path")

        source_name = "my_source"
        table_name = "my_table"
        returned_table_ref = "db.my_model"

        mocked_get_source_metadata = mocker.patch(
            "sql_mock.dbt._get_source_metadata"
        )
        mocked_get_source_metadata.return_value = {"table_ref": returned_table_ref}

        @dbt_source_meta(source_name=source_name, table_name=table_name, project_path=project_path)
        class TestMock(BaseTableMock):
            pass

        assert TestMock._sql_mock_meta.query is None
        assert TestMock._sql_mock_meta.table_ref == returned_table_ref
        mocked_get_source_metadata.assert_called_once_with(
            project_path=project_path, source_name=source_name, table_name=table_name
        )

    def test_project_path_not_provided_but_set_in_config(self, mocker):
        """...then metadata should be extracted from the project path provided in the config"""
        project_path = "path/to/my/project"
        SQLMockConfig.set_dbt_project_path(project_path)

        source_name = "my_source"
        table_name = "my_table"
        returned_table_ref = "db.my_model"

        mocked_get_source_metadata = mocker.patch(
            "sql_mock.dbt._get_source_metadata"
        )
        mocked_get_source_metadata.return_value = {"table_ref": returned_table_ref}

        @dbt_source_meta(source_name=source_name, table_name=table_name, project_path=project_path)
        class TestMock(BaseTableMock):
            pass

        assert TestMock._sql_mock_meta.query is None
        assert TestMock._sql_mock_meta.table_ref == returned_table_ref
        mocked_get_source_metadata.assert_called_once_with(
            project_path=project_path, source_name=source_name, table_name=table_name
        )


class TestDbtSeedMeta:
    def test_project_path_provided(self, mocker):
        """...then metadata should be extracted from that project path"""
        project_path = "path/to/my/project"

        # We set another path in the config but it should be overwritten
        SQLMockConfig.set_dbt_project_path("some/other/path")

        seed_name = "my_model"
        returned_query_path = "some/path/to/query.sql"
        returned_table_ref = "db.my_model"

        mocked_get_seed_metadata = mocker.patch("sql_mock.dbt._get_seed_metadata")
        mocked_get_seed_metadata.return_value = {
            "query_path": returned_query_path,
            "table_ref": returned_table_ref,
        }

        @dbt_seed_meta(seed_name=seed_name, project_path=project_path)
        class TestMock(BaseTableMock):
            pass

        assert TestMock._sql_mock_meta.query is None
        assert TestMock._sql_mock_meta.table_ref == returned_table_ref
        mocked_get_seed_metadata.assert_called_once_with(
            project_path=project_path, seed_name=seed_name
        )

    def test_project_path_not_provided_but_set_in_config(self, mocker):
        """...then metadata should be extracted from the project path provided in the config"""
        project_path = "path/to/my/project"
        SQLMockConfig.set_dbt_project_path(project_path)

        seed_name = "my_model"
        returned_query_path = "some/path/to/query.sql"
        returned_table_ref = "db.my_model"

        mocked_get_seed_metadata = mocker.patch("sql_mock.dbt._get_seed_metadata")
        mocked_get_seed_metadata.return_value = {
            "query_path": returned_query_path,
            "table_ref": returned_table_ref,
        }

        @dbt_seed_meta(seed_name=seed_name)
        class TestMock(BaseTableMock):
            pass

        assert TestMock._sql_mock_meta.query is None
        assert TestMock._sql_mock_meta.table_ref == returned_table_ref
        mocked_get_seed_metadata.assert_called_once_with(
            project_path=project_path, seed_name=seed_name
        )


PROJECT_FILE = "./tests/resources/dbt/dbt_project.yml"


class TestGetModelMetadata:
    def test_model_does_not_exist_in_file(self):
        """...then the method should raise a ValueError"""
        with pytest.raises(ValueError):
            _get_model_metadata(project_path=PROJECT_FILE, model_name="I don not exist")

    def test_model_does_exist_in_file(self):
        """...then the method should return the correct values"""
        data = _get_model_metadata(project_path=PROJECT_FILE, model_name="my_first_dbt_model")

        assert data["query_path"] == "./tests/resources/dbt/dbt_target/compiled_example_models/my_first_dbt_model.sql"
        assert data["table_ref"] == "`sql_mock_db`.`my_first_dbt_model`"


class TestGetSourceMetadata:
    def test_source_does_not_exist_in_file(self):
        """...then the method should raise a ValueError"""
        with pytest.raises(ValueError):
            _get_source_metadata(
                project_path=PROJECT_FILE, source_name="I don not exist", table_name="I don not exist either"
            )

    def test_source_does_exist_in_file(self):
        """...then the method should return the correct values"""
        data = _get_source_metadata(
            project_path=PROJECT_FILE, source_name="source_data", table_name="opportunity_events"
        )

        assert data["table_ref"] == "`source_data`.`opportunity_events`"


class TestGetSeedMetadata:
    def test_seed_does_not_exist_in_file(self):
        """...then the method should raise a ValueError"""
        with pytest.raises(ValueError):
            _get_seed_metadata(
                project_path=PROJECT_FILE,
                seed_name="I don not exist",
            )

    def test_seed_does_exist_in_file(self):
        """...then the method should return the correct values"""
        data = _get_seed_metadata(
            project_path=PROJECT_FILE,
            seed_name="country_codes",
        )

        assert data["table_ref"] == "`sql_mock_db`.`country_codes`"
