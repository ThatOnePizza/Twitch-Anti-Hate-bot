# Twitch Anti Hate bot
This bot has been quickly created to manage the issue of hate bots on Twitch.  
It allows a single streamer to manage mass bans. It also helps in communities who share trusted moderation to coordinate bans

## Commands

- `hello`: just a test/hello world command
    - Aliases: `world`, `test` 
- `run_bans`: Can be ran to ban the current database of nicknames. Suggested to run when first adding the bot and periodically if sharing the bot with a community
    - Aliases: `init`
- `ban`: Bans a user or a list of users (separated by a space, `user1 user2 user3`) and adds it/them to the database
    - Aliases: `add_ban`
- `check`: Automatically matches regex to check automatic bans. THIS WILL ONLY LIST POTENTIAL BANS
- `please`:  Runs the same check as above but now also bans them. RUN THIS COMMAND ONLY AFTER CHECKING THE LIST FROM THE ABOVE COMMAND

## Before running
Install `pipenv` (on Arch `python-pipenv`) from and run:
```
pipenv install
```

## How to Run
First, add the .txt file to the database. **One user per line**
```
pipenv run python txt2db.py bans.txt
```
You can repeast the step above with how many .txt files you want as long as they are formatted as indicated.

Rename `.env.template` to `.env` and edit the needed parameters

Run the bot with
```
pipenv run python run.py
```
