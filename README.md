# isabot

## About

Discord bot for AR Club's Discord Server. This bot will send weekly guild leaderboards of various types to the Discord server via webhook. Leaderboards may include: most number of mounts, most wins in Arenas/Battlegrounds, etc. For leaderboards in most wins in Arenas/Battlegrounds, this will be reset weekly at some particular date.

Data will be recorded in a cloud database.

The idea of having weekly leaderboards was inspired by [Ethan](https://github.com/EthanThatOneKid)'s [lc-dailies project.](https://github.com/acmcsufoss/lc-dailies)

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

### Essentials

This project requires the following software:

-   [Python 3.9](https://www.python.org/downloads/release/python-390/)
-   Text editor of your choice

Afterwards, set your .env file according to `.env.example`.

### Poetry

Install [Poetry, a tool for managing packages within a virtual environment.](https://python-poetry.org/)

Install packages: `poetry install`

Then, inject a plugin for Poetry called [Export](https://github.com/python-poetry/poetry-plugin-export). This plugin will help with exporting `poetry.lock` into other formats such as `requirements.txt`.

Use the below command to convert `poetry.lock` to `requirements.txt`:

```bash
poetry export -f requirements.txt --output requirements.txt --without-hashes
```

Run the server with: `poetry run start`

### Nix

Alternatively, you can use [Nix](https://nixos.org/) to setup the developer environment without manually downloading the required software (i.e Python 3.9, Poetry, etc)

> For beginners setting up Nix for the first time, see <https://nix.libdb.so/slides> for guidance.

After installation, run the following command at the root of this project:

```bash
nix-shell
```

After some use, [you can clean the Nix store](https://nlewo.github.io/nixos-manual-sphinx/administration/cleaning-store.xml.html) before using the shell if needed:

```bash
nix-collect-garbage
```

## Development

Use [ngrok](https://ngrok.com/) to test features that may require HTTPS such as OAuth:

```bash
# default port of app is 8000
# do not include https:// in <your assigned domain>
ngrok http --domain=<your assigned domain>.ngrok-free.app 8000
# or (if not using a domain)
ngrok http 8000
```

## Deployment

isabot can technically be deployed anywhere. Even better if using containers! However, the application and the deployment is geared towards the Google Cloud ecosystem. In the future, the project will be more flexible with deployments.

## Design Document

[Link to Google Document](https://docs.google.com/document/d/1CLyRQKKIdoB_0SqAfUjjma9gKK5hDBCVHVExUOhPM64/edit?usp=sharing)
