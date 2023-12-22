import os

import pytest
from google.cloud import bigquery
from pydantic import ValidationError

from sql_mock.bigquery.column_mocks import Int
from sql_mock.bigquery.table_mocks import BigQueryMockTable
from sql_mock.table_mocks import table_meta


@table_meta(table_ref="mock_test_table")
class MockTestTable(BigQueryMockTable):
    id = Int(default=1)


@pytest.fixture(autouse=True)
def patch_os_environment_variables(mocker):
    mocker.patch.dict(
        os.environ,
        {
            "GOOGLE_APPLICATION_CREDENTIALS": "example.json",
        },
        clear=True,
    )


def test_init_with_environment_variables(mocker):
    """...then the env vars should be used to set the attributes"""
    table = MockTestTable()
    assert table.settings.google_application_credentials == "example.json"


def test_init_with_missing_configs(mocker):
    """...then it should raise an error"""
    mocker.patch.dict(
        os.environ,
        {},
        clear=True,
    )
    with pytest.raises(ValidationError):
        MockTestTable()


def test_get_results(mocker):
    """Test the _get_results method."""
    # Create a mock query job result
    mock_query_job_result = [
        {"column1": "value1", "column2": "value2"},
        {"column1": "value3", "column2": "value4"}
        # Add more rows as needed
    ]
    query = "SELECT 1, 2"

    # Mock the Client and QueryJob classes and their methods
    mocker.patch("google.cloud.bigquery.Client")
    mock_client = bigquery.Client.return_value
    query_job_instance = mock_client.query.return_value
    query_job_instance.result.return_value = mock_query_job_result

    instance = BigQueryMockTable()
    result = instance._get_results(query=query)

    assert result == mock_query_job_result
    mock_client.query.assert_called_once_with(query)
