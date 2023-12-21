import pytest

from sql_mock.column_mocks import ColumnMock
from sql_mock.table_mocks import BaseMockTable, table_meta


class IntTestColumn(ColumnMock):
    dtype = "Integer"


class StringTestColumn(ColumnMock):
    dtype = "String"


@table_meta(table_ref="test_data")
class MockTestTable(BaseMockTable):
    name = StringTestColumn(default="Thomas")
    age = IntTestColumn(default=0)
    city = StringTestColumn(default="Munich")


_assert_equal_successful_test_cases = [
    "data, expected_data, ignore_missing_keys, ignore_order",  # Name of the parameters
    [
        pytest.param(
            [{"name": "Alice", "age": 25, "city": "New York"}, {"name": "Bob", "age": 30, "city": "Munich"}],  # data
            [
                {"name": "Bob", "age": 30, "city": "Munich"},
                {"name": "Alice", "age": 25, "city": "New York"},
            ],  # expected_data
            False,  # ignore_missing_keys
            True,  # ignore_order
            id="Matching data - Missing keys not ignored - Order ignored",
        ),
        pytest.param(
            [{"name": "Alice", "age": 25, "city": "New York"}, {"name": "Bob", "age": 30, "city": "Munich"}],  # data
            [{"name": "Bob", "age": 30}, {"name": "Alice", "age": 25}],  # expected_data
            True,  # ignore_missing_keys
            True,  # ignore_order
            id="Matching data - Missing keys ignored - Order ignored",
        ),
        pytest.param(
            [{"name": "Alice", "age": 25, "city": "New York"}, {"name": "Bob", "age": 30, "city": "Munich"}],  # data
            [{"name": "Alice", "age": 25}, {"name": "Bob", "age": 30}],  # expected_data
            True,  # ignore_missing_keys
            False,  # ignore_order
            id="Matching data - Missing keys ignored - Order not ignored",
        ),
    ],
]


@pytest.mark.parametrize(*_assert_equal_successful_test_cases)
def test__assert_equal_success(data, expected_data, ignore_missing_keys, ignore_order):
    instance = MockTestTable()
    instance._assert_equal(
        data=data, expected=expected_data, ignore_missing_keys=ignore_missing_keys, ignore_order=ignore_order
    )


_assert_equal_failing_test_cases = [
    "data, expected_data, ignore_missing_keys, ignore_order",  # Name of the parameters
    [
        pytest.param(
            [{"name": "Alice", "age": 25, "city": "New York"}, {"name": "Bob", "age": 30, "city": "Munich"}],  # data
            [
                {"name": "Not Alice", "age": 1, "city": "Not New York"},
                {"name": "Not Bob", "age": 2, "city": "Not Munich"},
            ],  # expected_data
            True,  # ignore_missing_keys
            True,  # ignore_order
            id="Data not matching - Missing keys ignored - Order ignored",
        ),
        pytest.param(
            [{"name": "Alice", "age": 25, "city": "New York"}, {"name": "Bob", "age": 30, "city": "Munich"}],  # data
            [{"name": "Bob", "age": 30}, {"name": "Alice", "age": 25}],  # expected_data
            False,  # ignore_missing_keys
            True,  # ignore_order
            id="Missing keys but ignore_missing_keys=False",
        ),
        pytest.param(
            [{"name": "Alice", "age": 25, "city": "New York"}, {"name": "Bob", "age": 30, "city": "Munich"}],  # data
            [
                {"name": "Bob", "age": 30, "city": "Munich"},
                {"name": "Alice", "age": 25, "city": "New York"},
            ],  # expected_data
            True,  # ignore_missing_keys
            False,  # ignore_order
            id="Matching data but order is not correct",
        ),
    ],
]


@pytest.mark.parametrize(*_assert_equal_failing_test_cases)
def test__assert_equal_raises(data, expected_data, ignore_missing_keys, ignore_order):
    instance = MockTestTable()

    with pytest.raises(AssertionError):
        instance._assert_equal(
            data=data, expected=expected_data, ignore_missing_keys=ignore_missing_keys, ignore_order=ignore_order
        )


_assert_equal_test_cases = [
    "ignore_missing_keys, ignore_order",  # Name of the parameters
    [
        pytest.param(
            False,  # ignore_missing_keys
            True,  # ignore_order
            id="Missing keys not ignored - Order ignored",
        ),
        pytest.param(
            True,  # ignore_missing_keys
            True,  # ignore_order
            id="Missing keys ignored - Order ignored",
        ),
        pytest.param(
            True,  # ignore_missing_keys
            False,  # ignore_order
            id="Missing keys ignored - Order not ignored",
        ),
    ],
]


@pytest.mark.parametrize(*_assert_equal_test_cases)
def test_assert_equal(mocker, ignore_missing_keys, ignore_order):
    instance = MockTestTable()
    data = ([{"name": "Alice", "age": 25, "city": "New York"}, {"name": "Bob", "age": 30, "city": "Munich"}],)
    mocker.patch.object(instance, "_get_results", return_value=data)
    mocker.patch.object(instance, "_generate_query", return_value="SELECT 1")  # We don't care about the query here
    mocked_assert_equal = mocker.patch.object(instance, "_assert_equal", return_value=None)

    instance.assert_equal(expected=data, ignore_missing_keys=ignore_missing_keys, ignore_order=ignore_order)

    mocked_assert_equal.assert_called_once_with(
        data=data,
        expected=data,
        ignore_missing_keys=ignore_missing_keys,
        ignore_order=ignore_order,
        print_query_on_fail=True,
    )


@pytest.mark.parametrize(*_assert_equal_test_cases)
def test_assert_cte_equal(mocker, ignore_missing_keys, ignore_order):
    instance = MockTestTable()
    cte_name = "some_cte"
    query = "SELECT 1"
    data = ([{"name": "Alice", "age": 25, "city": "New York"}, {"name": "Bob", "age": 30, "city": "Munich"}],)
    mocker.patch.object(instance, "_get_results", return_value=data)
    mocked_generate_query = mocker.patch.object(
        instance, "_generate_query", return_value=query
    )  # We don't care about the query here
    mocked_assert_equal = mocker.patch.object(instance, "_assert_equal", return_value=None)

    instance.assert_cte_equal(
        cte_name=cte_name, expected=data, ignore_missing_keys=ignore_missing_keys, ignore_order=ignore_order
    )

    mocked_assert_equal.assert_called_once_with(
        data=data,
        expected=data,
        ignore_missing_keys=ignore_missing_keys,
        ignore_order=ignore_order,
        print_query_on_fail=True,
    )
    mocked_generate_query.assert_called_once_with(cte_to_select=cte_name)
