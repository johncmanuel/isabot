# Isabot

Discord bot for AR Club's Discord Server. This bot will send weekly guild leaderboards of various types to the Discord server via webhook. Leaderboards may include: most number of mounts, most wins in Arenas/Battlegrounds, etc. For leaderboards in most wins in Arenas/Battlegrounds, this will be reset weekly at some particular date.

All of the data will be recorded in a cloud database (most likely Google's Firestore).

The idea of having weekly leaderboards was inspired by Ethan's [lc-dailies project.](https://github.com/acmcsufoss/lc-dailies)

## Technology

1. [FastAPI](https://fastapi.tiangolo.com/)
2. [Discord API and webhooks](https://discord.com/developers/docs/intro)
3. [Blizzard's WoW API](https://develop.battle.net/documentation/world-of-warcraft)

## Getting Started

Install packages: `poetry install`

Run the server with: `poetry run uvicorn main:app --reload`

If you choose not to use build tools such as Poetry, perform the following operations:

```bash
pip install
uvicorn main:app --reload
```
