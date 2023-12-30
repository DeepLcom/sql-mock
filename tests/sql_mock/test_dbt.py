import pytest

from sql_mock.config import SQLMockConfig
from sql_mock.dbt import (
    _get_model_metadata_from_dbt_manifest,
    _get_seed_metadata_from_dbt_manifest,
    _get_source_metadata_from_dbt_manifest,
    dbt_model_meta,
    dbt_seed_meta,
    dbt_source_meta,
)
from sql_mock.table_mocks import BaseMockTable


class TestDbtModelMeta:
    def test_manifest_path_provided(self, mocker):
        """...then metadata should be extracted from that manifest path"""
        manifest_path = "path/to/my/manifest"

        # We set another path in the config but it should be overwritten
        SQLMockConfig.set_dbt_manifest_path("some/other/path")

        model_name = "my_model"
        returned_query_path = "some/path/to/query.sql"
        returned_table_ref = "db.my_model"

        mocked_get_model_metadata_from_dbt_manifest = mocker.patch(
            "sql_mock.dbt._get_model_metadata_from_dbt_manifest"
        )
        mocked_get_model_metadata_from_dbt_manifest.return_value = {
            "query_path": returned_query_path,
            "table_ref": returned_table_ref,
        }

        query = "SELECT bar FROM foo"
        mock_open = mocker.patch("builtins.open")
        # Configure the mock to return the file content
        mock_open.return_value.__enter__.return_value.read.return_value = query

        @dbt_model_meta(model_name=model_name, manifest_path=manifest_path)
        class TestMock(BaseMockTable):
            pass

        assert TestMock._sql_mock_meta.query == query
        assert TestMock._sql_mock_meta.table_ref == returned_table_ref
        mock_open.assert_called_once_with(returned_query_path)
        mocked_get_model_metadata_from_dbt_manifest.assert_called_once_with(
            manifest_path=manifest_path, model_name=model_name
        )

    def test_manifest_path_not_provided_but_set_in_config(self, mocker):
        """...then metadata should be extracted from the manifest path provided in the config"""
        manifest_path = "path/to/my/manifest"
        SQLMockConfig.set_dbt_manifest_path(manifest_path)

        model_name = "my_model"
        returned_query_path = "some/path/to/query.sql"
        returned_table_ref = "db.my_model"

        mocked_get_model_metadata_from_dbt_manifest = mocker.patch(
            "sql_mock.dbt._get_model_metadata_from_dbt_manifest"
        )
        mocked_get_model_metadata_from_dbt_manifest.return_value = {
            "query_path": returned_query_path,
            "table_ref": returned_table_ref,
        }

        query = "SELECT bar FROM foo"
        mock_open = mocker.patch("builtins.open")
        # Configure the mock to return the file content
        mock_open.return_value.__enter__.return_value.read.return_value = query

        @dbt_model_meta(model_name=model_name)
        class TestMock(BaseMockTable):
            pass

        assert TestMock._sql_mock_meta.query == query
        assert TestMock._sql_mock_meta.table_ref == returned_table_ref
        mock_open.assert_called_once_with(returned_query_path)
        mocked_get_model_metadata_from_dbt_manifest.assert_called_once_with(
            manifest_path=manifest_path, model_name=model_name
        )


class TestDbtSourceMeta:
    def test_manifest_path_provided(self, mocker):
        """...then metadata should be extracted from that manifest path"""
        manifest_path = "path/to/my/manifest"

        # We set another path in the config but it should be overwritten
        SQLMockConfig.set_dbt_manifest_path("some/other/path")

        source_name = "my_source"
        table_name = "my_table"
        returned_table_ref = "db.my_model"

        mocked_get_source_metadata_from_dbt_manifest = mocker.patch(
            "sql_mock.dbt._get_source_metadata_from_dbt_manifest"
        )
        mocked_get_source_metadata_from_dbt_manifest.return_value = {"table_ref": returned_table_ref}

        @dbt_source_meta(source_name=source_name, table_name=table_name, manifest_path=manifest_path)
        class TestMock(BaseMockTable):
            pass

        assert TestMock._sql_mock_meta.query is None
        assert TestMock._sql_mock_meta.table_ref == returned_table_ref
        mocked_get_source_metadata_from_dbt_manifest.assert_called_once_with(
            manifest_path=manifest_path, source_name=source_name, table_name=table_name
        )

    def test_manifest_path_not_provided_but_set_in_config(self, mocker):
        """...then metadata should be extracted from the manifest path provided in the config"""
        manifest_path = "path/to/my/manifest"
        SQLMockConfig.set_dbt_manifest_path(manifest_path)

        source_name = "my_source"
        table_name = "my_table"
        returned_table_ref = "db.my_model"

        mocked_get_source_metadata_from_dbt_manifest = mocker.patch(
            "sql_mock.dbt._get_source_metadata_from_dbt_manifest"
        )
        mocked_get_source_metadata_from_dbt_manifest.return_value = {"table_ref": returned_table_ref}

        @dbt_source_meta(source_name=source_name, table_name=table_name, manifest_path=manifest_path)
        class TestMock(BaseMockTable):
            pass

        assert TestMock._sql_mock_meta.query is None
        assert TestMock._sql_mock_meta.table_ref == returned_table_ref
        mocked_get_source_metadata_from_dbt_manifest.assert_called_once_with(
            manifest_path=manifest_path, source_name=source_name, table_name=table_name
        )


class TestDbtSeedMeta:
    def test_manifest_path_provided(self, mocker):
        """...then metadata should be extracted from that manifest path"""
        manifest_path = "path/to/my/manifest"

        # We set another path in the config but it should be overwritten
        SQLMockConfig.set_dbt_manifest_path("some/other/path")

        seed_name = "my_model"
        returned_query_path = "some/path/to/query.sql"
        returned_table_ref = "db.my_model"

        mocked_get_seed_metadata_from_dbt_manifest = mocker.patch("sql_mock.dbt._get_seed_metadata_from_dbt_manifest")
        mocked_get_seed_metadata_from_dbt_manifest.return_value = {
            "query_path": returned_query_path,
            "table_ref": returned_table_ref,
        }

        @dbt_seed_meta(seed_name=seed_name, manifest_path=manifest_path)
        class TestMock(BaseMockTable):
            pass

        assert TestMock._sql_mock_meta.query is None
        assert TestMock._sql_mock_meta.table_ref == returned_table_ref
        mocked_get_seed_metadata_from_dbt_manifest.assert_called_once_with(
            manifest_path=manifest_path, seed_name=seed_name
        )

    def test_manifest_path_not_provided_but_set_in_config(self, mocker):
        """...then metadata should be extracted from the manifest path provided in the config"""
        manifest_path = "path/to/my/manifest"
        SQLMockConfig.set_dbt_manifest_path(manifest_path)

        seed_name = "my_model"
        returned_query_path = "some/path/to/query.sql"
        returned_table_ref = "db.my_model"

        mocked_get_seed_metadata_from_dbt_manifest = mocker.patch("sql_mock.dbt._get_seed_metadata_from_dbt_manifest")
        mocked_get_seed_metadata_from_dbt_manifest.return_value = {
            "query_path": returned_query_path,
            "table_ref": returned_table_ref,
        }

        @dbt_seed_meta(seed_name=seed_name)
        class TestMock(BaseMockTable):
            pass

        assert TestMock._sql_mock_meta.query is None
        assert TestMock._sql_mock_meta.table_ref == returned_table_ref
        mocked_get_seed_metadata_from_dbt_manifest.assert_called_once_with(
            manifest_path=manifest_path, seed_name=seed_name
        )


MANIFEST_FILE = "./tests/resources/dbt/dbt_manifest.json"


class TestGetModelMetadataDbtFromManifest:
    def test_model_does_not_exist_in_file(self):
        """...then the method should raise a ValueError"""
        with pytest.raises(ValueError):
            _get_model_metadata_from_dbt_manifest(manifest_path=MANIFEST_FILE, model_name="I don not exist")

    def test_model_does_exist_in_file(self):
        """...then the method should return the correct values"""
        data = _get_model_metadata_from_dbt_manifest(manifest_path=MANIFEST_FILE, model_name="my_first_dbt_model")

        assert data["query_path"] == "tests/resources/dbt/compiled_example_models/my_first_dbt_model.sql"
        assert data["table_ref"] == "`sql_mock_db`.`my_first_dbt_model`"


class TestGetSourceMetadataDbtFromManifest:
    def test_source_does_not_exist_in_file(self):
        """...then the method should raise a ValueError"""
        with pytest.raises(ValueError):
            _get_source_metadata_from_dbt_manifest(
                manifest_path=MANIFEST_FILE, source_name="I don not exist", table_name="I don not exist either"
            )

    def test_source_does_exist_in_file(self):
        """...then the method should return the correct values"""
        data = _get_source_metadata_from_dbt_manifest(
            manifest_path=MANIFEST_FILE, source_name="source_data", table_name="opportunity_events"
        )

        assert data["table_ref"] == "`source_data`.`opportunity_events`"


class TestGetSeedMetadataDbtFromManifest:
    def test_seed_does_not_exist_in_file(self):
        """...then the method should raise a ValueError"""
        with pytest.raises(ValueError):
            _get_seed_metadata_from_dbt_manifest(
                manifest_path=MANIFEST_FILE,
                seed_name="I don not exist",
            )

    def test_seed_does_exist_in_file(self):
        """...then the method should return the correct values"""
        data = _get_seed_metadata_from_dbt_manifest(
            manifest_path=MANIFEST_FILE,
            seed_name="country_codes",
        )

        assert data["table_ref"] == "`sql_mock_db`.`country_codes`"
