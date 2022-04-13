<h1 align="center">Discord Reddit Bot</h1>
<p align="center">Channel Reddit Poster</p>

--------
[![Python 3.10](https://img.shields.io/badge/python-3.10-yellow.svg)](https://www.python.org)
[![Black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/ambv/black)
[![Python 3.10](https://img.shields.io/badge/docker-alpine-blue.svg)](https://www.python.org)

## What is this bot for?

Run the `!sub subreddit` command in a channel to stream the lastest submissions from the subreddit you specify.

## Table of contents

- [Quick Start](#quick-start)
- [Local Deploy Steps](#local-deploy-steps)
- [Notes](#notes)

## Quick start

- Download the repo.

## Local Deploy steps

Install the required dependencies:

    $ pip install -r requirements/local.txt

Set up environment variables:

    $ cp .env.example .env

## Notes

To run bot:

	$ docker-compose up -d --build 

To remove bot:

	$ docker-compose down

Once the bot is running use the `!help` command to see the available commands.

