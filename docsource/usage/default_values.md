```{toctree}
:maxdepth: 2
```

# Default values

Testing SQL queries can often involve repetitive setup for mock tables. In SQLMock, one effective way to streamline this process is by using default values. By setting reasonable defaults, you can significantly reduce the boilerplate code in your tests, especially when dealing with multiple input tables or complex queries. Let’s explore how you can efficiently implement this.

## Utilizing Default Values in MockTable Fields

Defining default values at the field level in your mock tables is straightforward.
The default argument in the field definition allows you to set default values consistency across all test scenarios in one step. 
They are particularly useful for ensuring that joins and other query functionalities operate correctly.

Here's an example:

```python 
@table_meta(table_ref="data.users")
class UserTable(BigQueryMockTable):
    user_id = col.Int(default=1)
    user_name = col.String(default="Mr. T")

# Create instances of the UserTable with various combinations of defaults and specified values
users = UserTable.from_dicts([
    {}, # Left empty {} uses default values --> {"user_id": 1, "user_name": "Mr. T"}
    {"user_id": 2}, # Overrides user_id but uses default for user_name
    {"user_id": 3, "user_name": "Nala"} # No defaults used here
])
```

## Setting Mock Defaults with table_meta


When defining your MockTable classes, the `table_meta` decorator accepts a `default_inputs` argument.
The Mock instances passed here, will be used as defaults in the `from_mocks` method.

Consider this example:

```python 
@table_meta(
    query_path="./examples/test_query.sql",
    default_inputs=[UserTable([]), SubscriptionTable([])] # We can provide defaults for the class if needed.
)
class MultipleSubscriptionUsersTable(BigQueryMockTable):
    user_id = col.Int(default=1)

# Setting up different scenarios to demonstrate the use of defaults
users = UserTable.from_dicts([
    {"user_id": 1}, 
    {"user_id": 2}
])
subscriptions = SubscriptionTable.from_dicts(
    [
        {"subscription_id": 1, "user_id": 1},
        {"subscription_id": 2, "user_id": 1},
        {"subscription_id": 2, "user_id": 2},
    ]
)

# Utilizing the default inputs set in the table_meta
res = MultipleSubscriptionUsersTable.from_mocks(input_data=[])
res = MultipleSubscriptionUsersTable.from_mocks(input_data=[users]) # Using only users, defaults for others
res = MultipleSubscriptionUsersTable.from_mocks(input_data=[users, subscriptions]) # Overriding defaults
```

## When is this useful?

* **Safe time and code by changing only the data you need for your test case:** You can only change single columns for the data you provide for a test case. The rest will be filled by defaults.
* **Simplifying Happy Path Testing:** Validate basic functionality and syntax correctness of your SQL queries with minimal setup.
* **Testing Subset Logic:** When certain tables in your query don't require data, default values can help focus on specific test scenarios.
* **Provide reasonable defaults for joins:** In tests with numerous input tables you can specify inputs that joins between tables work. For frequent addition of new tables, defaults can prevent the need for extensive refactoring.
