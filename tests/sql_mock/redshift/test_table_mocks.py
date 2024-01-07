import os

import pytest
from pydantic import ValidationError

from sql_mock.redshift.column_mocks import BIGINT
from sql_mock.redshift.table_mocks import RedshiftMockTable
from sql_mock.table_mocks import table_meta


@table_meta(table_ref="mock_test_table")
class MockTestTable(RedshiftMockTable):
    id = BIGINT(default=1)


@pytest.fixture(autouse=True)
def patch_os_environment_variables(mocker):
    mocker.patch.dict(
        os.environ,
        {
            "SQL_MOCK_REDSHIFT_HOST": "localhost",
            "SQL_MOCK_REDSHIFT_DATABASE": "test_db",
            "SQL_MOCK_REDSHIFT_USER": "test_user",
            "SQL_MOCK_REDSHIFT_PASSWORD": "test_pw",
        },
        clear=True,
    )


def test_init_with_environment_variables(mocker):
    """...then the env vars should be used to set the attributes"""
    table = MockTestTable()
    assert table.settings.host == "localhost"
    assert table.settings.database == "test_db"
    assert table.settings.user == "test_user"
    assert table.settings.password == "test_pw"


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
    # Mock the Redshift connector and the fetch_dataframe method from the following code:
    mock_connector = mocker.patch("sql_mock.redshift.table_mocks.redshift_connector")
    mocked_connect = mock_connector.connect.return_value.__enter__.return_value
    mocked_cursor = mocked_connect.cursor.return_value.__enter__.return_value
    mocked_execute = mocked_cursor.execute
    mocked_fetch_dataframe = mocked_cursor.fetch_dataframe
    mock_dataframe = mocker.MagicMock()
    mock_dataframe.to_dict.return_value = mock_query_job_result
    mocked_fetch_dataframe.return_value = mock_dataframe

    instance = RedshiftMockTable()
    result = instance._get_results(query=query)

    assert result == mock_query_job_result
    mocked_execute.assert_called_once_with(query)
