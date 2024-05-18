from isabot.api.leaderboards.data_types import Entry

# TODO: Use below mock data for making tests in future
mock_entry1 = Entry(
    players={
        "12345678": {"battletag": "player1", "id": "12345678"},
        "87654321": {"battletag": "player2", "id": "87654321"},
        "98765432": {"battletag": "player3", "id": "98765432"},
    },
    date_created=1643347200.0,
    mounts={
        "12345678": {"number_of_mounts": 1238},
        "87654321": {"number_of_mounts": 38482},
        "98765432": {"number_of_mounts": 20},
    },
    normal_bg_wins={
        "12345678": {
            "bg_total_won": 120,
            "bg_total_lost": 20,
            "user_id": "12345678",
        },
        "87654321": {
            "bg_total_won": 80,
            "bg_total_lost": 50,
            "user_id": "87654321",
        },
        "98765432": {
            "bg_total_won": 200,
            "bg_total_lost": 30,
            "user_id": "98765432",
        },
    },
)
