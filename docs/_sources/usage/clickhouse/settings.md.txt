```{toctree}
:maxdepth: 2
```

# Settings

In order to use SQL Mock with Clickhouse, you need to provide the following environment variables when you run tests: 
* `SQL_MOCK_CLICKHOUSE_HOST`: Host of your Clickhouse instance
* `SQL_MOCK_CLICKHOUSE_USER`: User you want to use for the connection
* `SQL_MOCK_CLICKHOUSE_PASSWORD`: Password of your user
* `SQL_MOCK_CLICKHOUSE_PORT`: Port of your Clickhouse instance

Having those environment variables enables SQL Mock to connect to your Clickhouse instance.
