<h1 align="center">Discord Reddit Bot</h1>
<p align="center">Channel Reddit Poster</p>

## What is this bot for?

Run the `!sub subreddit` command in a channel to retrieve the newest post every minute from the subreddit you specify.

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

