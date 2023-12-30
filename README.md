# isabot

## About

Discord bot for AR Club's Discord Server. This bot will send weekly guild leaderboards of various types to the Discord server via webhook. Leaderboards may include: most number of mounts, most wins in Arenas/Battlegrounds, etc. For leaderboards in most wins in Arenas/Battlegrounds, this will be reset weekly at some particular date.

All of the data will be recorded in a cloud database (most likely Google's Firestore).

The idea of having weekly leaderboards was inspired by Ethan's [lc-dailies project.](https://github.com/acmcsufoss/lc-dailies)


## Purpose

The purpose of Isabot is to promote friendly competition within the guild, recognize other guildies' hard work, and an overall sense of community.   

## Technology

1. [FastAPI](https://fastapi.tiangolo.com/)
2. [Discord API and webhooks](https://discord.com/developers/docs/intro)
3. [Blizzard's WoW API](https://develop.battle.net/documentation/world-of-warcraft)

## Getting Started

Install [Poetry, a tool for managing packages within a virtual environment.](https://python-poetry.org/)

Install packages: `poetry install`

Then, inject a plugin for Poetry called [Export](https://github.com/python-poetry/poetry-plugin-export). This plugin will help with exporting `poetry.lock` into other formats such as `requirements.txt`.

Use the below command to convert `poetry.lock` to `requirements.txt`:

```bash
poetry export -f requirements.txt --output requirements.txt --without-hashes
```

Run the server with: `poetry run uvicorn main:app --reload`

## Development

Use [ngrok](https://ngrok.com/) to test features such as OAuth:

```bash
# default port of app is 8000
# do not include https://
ngrok http --domain=<your assigned domain>.ngrok-free.app 8000
# or (if not using a domain)
ngrok http 8000
```
