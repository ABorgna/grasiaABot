GrasiaABot 
==========
_A reddit bot to say grasia_

Matches a list of regexes over every comment in the defined subreddits, and posts a reply.

Requires python3 and python3-praw.

Quick start
-----------
Run `python3 src/grasia.py` to generate the default `config.cfg`, and fill the username, password and subreddits (comma-delimited).

To have the bot always running, starting it on reboot, add this line to the crontab (with `crontab -e`)
```
@reboot /path/to/grasiaABot/run.sh
```
