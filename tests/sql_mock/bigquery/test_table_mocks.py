import os

import pytest
from google.cloud import bigquery
from pydantic import ValidationError

from sql_mock.bigquery.column_mocks import Int
from sql_mock.bigquery.table_mocks import BigQueryMockTable


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
    table = BigQueryMockTable()
    assert table.settings.google_application_credentials == "example.json"


def test_init_with_missing_configs(mocker):
    """...then it should raise an error"""
    mocker.patch.dict(
        os.environ,
        {},
        clear=True,
    )
    with pytest.raises(ValidationError):
        BigQueryMockTable()


def test_get_results(mocker):
    """Test the _get_results method."""
    # Create a mock query job result
    mock_query_job_result = [
        {"column1": "value1", "column2": "value2"},
        {"column1": "value3", "column2": "value4"}
        # Add more rows as needed
    ]

    # Mock the Client and QueryJob classes and their methods
    mocker.patch("google.cloud.bigquery.Client")
    mock_client = bigquery.Client.return_value
    query_job_instance = mock_client.query.return_value
    query_job_instance.result.return_value = mock_query_job_result

    result = BigQueryMockTable.from_inputs(query="SELECT 1", input_data={"foo.bar": MockTestTable(data=[])})

    # Assert the result matches the expected mock result
    result.assert_equal(mock_query_job_result)
