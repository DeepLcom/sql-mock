from sql_mock.bigquery import column_mocks as col
from sql_mock.bigquery.table_mocks import BigQueryMockTable
from sql_mock.config import SQLMockConfig
from sql_mock.dbt import dbt_model_meta, dbt_seed_meta, dbt_source_meta

SQLMockConfig.set_dbt_manifest_path("./tests/resources/dbt/dbt_manifest.json")


# NOTE: The Source and Seed classes will not be used in the example test. They are only here for demonstration purpose.
@dbt_source_meta(source_name="source_data", table_name="opportunity_events")
class OpportunityEventsSource(BigQueryMockTable):
    event_id = col.Int(default=1)
    event_type = col.String(default="foo")
    event_date = col.Date(default="2023-12-24")


@dbt_seed_meta(seed_name="country_codes")
class CountryCodesSeed(BigQueryMockTable):
    country_code = col.String(default="foo")
    country_name = col.String(default="foo")


@dbt_model_meta(model_name="my_first_dbt_model")
class MyFirstDBTModel(BigQueryMockTable):
    id = col.Int(default=1)


@dbt_model_meta(model_name="my_second_dbt_model")
class MySecondDBTModel(BigQueryMockTable):
    id = col.Int(default=1)


def test_my_second_dbt_model():
    # Mock data for the first model
    first_model_data = [{"id": 1}, {"id": 2}, {"id": 3}]

    # Create a mock table instance with the data
    first_model_table = MyFirstDBTModel.from_dicts(first_model_data)

    # Expected result for the second model
    expected_output = [{"id": 1}]  # Assuming the second model filters for entries with id 1 only

    # Instantiate the second dbt model mock table with the first model as input
    second_model_table = MySecondDBTModel.from_mocks(input_data=[first_model_table])

    # Assert that the dbt model's output matches the expected output
    second_model_table.assert_equal(expected_output)
