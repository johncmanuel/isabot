# isabot

## About

Discord bot for AR Club's Discord Server. This bot will send weekly guild leaderboards of various types to the Discord server via webhook. Leaderboards may include: most number of mounts, most wins in Arenas/Battlegrounds, etc. For leaderboards in most wins in Arenas/Battlegrounds, this will be reset weekly at some particular date.

Data will be recorded in a cloud database.

The idea of having weekly leaderboards was inspired by Ethan's [lc-dailies project.](https://github.com/acmcsufoss/lc-dailies)

## Purpose

The purpose of Isabot is to promote friendly competition within the guild, recognize other guildies' hard work, and an overall sense of community.

## Technology

1. [FastAPI (web server)](https://fastapi.tiangolo.com/)
2. [Discord API and webhooks](https://discord.com/developers/docs/intro)
3. [Blizzard API](https://develop.battle.net/documentation/battle-net)
4. [Google Cloud Run (deployment)](https://cloud.google.com/run)
5. [Google Cloud Build (CI/CD)](https://cloud.google.com/build?hl=en)
6. [Google Cloud Scheduler (for running cron jobs)](https://cloud.google.com/scheduler)
7. [Google Cloud Secret Manager (for storing production secrets)](https://cloud.google.com/security/products/secret-manager)
8. [Google Firestore (NoSQL)](https://cloud.google.com/firestore?hl=en)

## Getting Started

### Poetry

Install [Poetry, a tool for managing packages within a virtual environment.](https://python-poetry.org/)

Install packages: `poetry install`

Then, inject a plugin for Poetry called [Export](https://github.com/python-poetry/poetry-plugin-export). This plugin will help with exporting `poetry.lock` into other formats such as `requirements.txt`.

Use the below command to convert `poetry.lock` to `requirements.txt`:

```bash
poetry export -f requirements.txt --output requirements.txt --without-hashes
```

Run the server with: `poetry run uvicorn main:app --reload`

> NOTE: The default port number is 8000.

### Nix

WIP

## Development

Use [ngrok](https://ngrok.com/) to test features such as OAuth:

```bash
# default port of app is 8000
# do not include https:// in <your assigned domain>
ngrok http --domain=<your assigned domain>.ngrok-free.app 8000
# or (if not using a domain)
ngrok http 8000
```

## Deployment

isabot can technically be deployed anywhere. Even better if using containers! However, the application and the deployment is geared towards the Google Cloud ecosystem. In the future, the project will be more flexible with deployments.

## Design Document (contains list of endpoints)

[Link to Google Document](https://docs.google.com/document/d/1CLyRQKKIdoB_0SqAfUjjma9gKK5hDBCVHVExUOhPM64/edit?usp=sharing)
