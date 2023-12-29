# Enhanced SQLMock with dbt Integration Guide

## Introduction

This guide will provide a quick start on how to use SQLMock with dbt (data build tool). You can use it to mock dbt models, sources, and seed models. We'll cover how to use these features effectively in your unit tests.

## Prerequisites

- A working dbt project with a `manifest.json` file **that has the latest compiled run.** (make sure to run `dbt compile`).
- The SQLMock library installed in your Python environment.

## Configuration

### Setting the dbt Manifest Path

Initialize your testing environment by setting the global path to your dbt manifest file:

```python
from sql_mock.config import SQLMockConfig

SQLMockConfig.set_dbt_manifest_path('/path/to/your/dbt/manifest.json')
```

## Creating Mock Tables

SQLMock offers specialized decorators for different dbt entities: models, sources, and seeds.

### dbt Model Mock Table

For dbt models, use the `dbt_model_meta` decorator from `sql_mock.dbt`. This decorator is suited for mocking the transformed data produced by dbt models.

```python
from sql_mock.dbt import dbt_model_meta
from sql_mock.bigquery.table_mocks import BigQueryMockTable

@dbt_model_meta(model_name="your_dbt_model_name")
class YourDBTModelTable(BigQueryMockTable):
    # Define your table columns and other necessary attributes here
    ...
```

### dbt Source Mock Table

For dbt sources, use the `dbt_source_meta` decorator from `sql_mock.dbt`. This is ideal for mocking the raw data sources that dbt models consume.

```python
from sql_mock.dbt import dbt_source_meta
from sql_mock.bigquery.table_mocks import BigQueryMockTable

@dbt_source_meta(source_name="your_source_name", table_name="your_source_table")
class YourDBTSourceTable(BigQueryMockTable):
    # Define your table columns and other necessary attributes here
    ...
```

### dbt Seed Mock Table

For dbt seeds, which are static data sets loaded into the database, use the `dbt_seed_meta` decorator from `sql_mock.dbt`.

```python
from sql_mock.dbt import dbt_seed_meta
from sql_mock.bigquery.table_mocks import BigQueryMockTable

@dbt_seed_meta(seed_name="your_dbt_seed_name")
class YourDBTSeedTable(BigQueryMockTable):
    # Define your table columns and other necessary attributes here
    ...
```

## Example: Testing a dbt Model with Upstream Source and Seed Data

Let’s consider a dbt model named `monthly_user_spend` that aggregates data from a source `user_transactions` and a seed `user_categories`.

### Step 1: Define Your Source and Seed Mock Tables

```python
@dbt_source_meta(source_name="transactions", table_name="user_transactions")
class UserTransactionsTable(BigQueryMockTable):
    transaction_id = col.Int(default=1)
    user_id = col.Int(default=1)
    amount = col.Float(default=1.0)
    transaction_date = col.Date(default='2023-12-24')

@dbt_seed_meta(seed_name="user_categories")
class UserCategoriesTable(BigQueryMockTable):
    user_id = col.Int(default=1)
    category = col.String(default='foo')
```

### Step 2: Define Your Model Mock Table

```python
@dbt_model_meta(model_name="monthly_user_spend")
class MonthlyUserSpendTable(BigQueryMockTable):
    user_id = col.Int(default=1)
    month = col.String(default='foo')
    total_spend = col.Float(default=1.0)
    category = col.String(default='foo')
```

### Step 3: Write Your Test Case

```python
import datetime

def test_monthly_user_spend_model():
    # Mock input data for UserTransactionsTable and UserCategoriesTable
    transactions_data = [
        {"transaction_id": 1, "user_id": 1, "amount": 120.0, "transaction_date": datetime.date(2023, 1, 10)},
        {"transaction_id": 2, "user_id": 2, "amount": 150.0, "transaction_date": datetime.date(2023, 1, 20)},
    ]

    categories_data = [
        {"user_id": 1, "category": "Premium"},
        {"user_id": 2, "category": "Standard"}
    ]

    transactions_table = UserTransactionsTable.from_dicts(transactions_data)
    categories_table = UserCategoriesTable.from_dicts(categories_data)

    # Expected result
    expected_output = [
        {"user_id": 1, "month": "2023-01", "total_spend": 120.0, "category": "Premium"},
        {"user_id": 2, "month": "2023-01", "total_spend": 150.0, "category": "Standard"},
    ]

    monthly_spend_table = MonthlyUserSpendTable.from_mocks(input_data=[transactions_table, categories_table])

    monthly_spend_table.assert_equal(expected_output)
```
