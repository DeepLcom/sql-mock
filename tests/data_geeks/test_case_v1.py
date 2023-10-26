from tests.data_geeks.models import DataGeeks, MeetupVisits, VisitCounts

with open("./tests/data_geeks/query_v1.sql") as f:
    query = f.read()


def test_multiple_geeks_with_visits_some_without():
    """...then the visit counts per geek should be correct"""
    geek_id_1 = 1
    geek_id_2 = 2
    geek_id_3 = 3
    geeks = DataGeeks.from_dicts(
        [
            {"data_geek_id": geek_id_1, "name": "Thorsten Schön"},
            {"data_geek_id": geek_id_2, "name": "Thomas Schmidt"},
            {"data_geek_id": geek_id_3},
        ]
    )

    visits = MeetupVisits.from_dicts(
        [{"data_geek_id": geek_id_1}, {"data_geek_id": geek_id_1}, {"data_geek_id": geek_id_2}]
    )

    expected = [
        {"data_geek_id": geek_id_1, "visit_count": 2, "name": "Thorsten Schön"},
        {"data_geek_id": geek_id_2, "visit_count": 1, "name": "Thomas Schmidt"},
        {"data_geek_id": geek_id_3, "visit_count": 0, "name": "Data Geek"},  # geek 3 should also have a count of 0
    ]

    res = VisitCounts.from_mocks(query=query, input_data=[geeks, visits])
    res.assert_equal(expected)
