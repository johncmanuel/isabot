"""
How the leaderboard system will work:

Registering users to the leaderboard
1. user will login through web server
2. add relevant data to DB
3. use said data to fill the current leaderboards in DB

Updating the leaderboard
1. Use FastAPI's background tasks, cron jobs, or other ways of performing background tasks 
to query each account's characters and update the relevant data for character's 
appropiate Battle Net account on the DB
2. Note that the leaderboard will use the account's data for the leaderboard,
not the individual character's data
3. Could refer to https://stackoverflow.com/a/53182080
for verifying request on a route that executes cron jobs


Sending the leaderboard data
1. Use discord's webhook to send the weekly leaderboards

"""


class Leaderboard:
    def __init__(self) -> None:
        pass
