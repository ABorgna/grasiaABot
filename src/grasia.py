import praw
import time
import configparser
import os.path
import sys
import re

log = lambda s : print(time.strftime("%m-%d %H:%M")+": "+s)

# Configuration

configName = "../config.cfg"
config = configparser.ConfigParser()
config["credentials"] = {"username": "",
                         "password": ""}
config["something"] = {"subreddits": ""} # Comma delimited
config["praw"] = {"refresh_time": "5000"}

if os.path.isfile(configName):
    config.read("config.cfg")
else:
    with open(configName, "w") as configFile:
        config.write(configFile)

if not config["credentials"]["username"] or not config["credentials"]["username"]:
    log("Set an username and password in "+configName)
    sys.exit(1)

if not config["something"]["subreddits"]:
    log("Specify some subreddits in "+configName)
    sys.exit(2)

if int(config["praw"]["refresh_time"]) < 2000:
    log("The refresh time is too short, using 2000 mS")
    config["praw"]["refresh_time"] = 2000

# Connect to reddit

username = config["credentials"]["username"]
password = config["credentials"]["password"]

reddit = praw.Reddit("grasiabot"
                     "Url:github.com/ABorgna/graciaabot")
reddit.login(username=username,password=password)

# Beware of the regular expressions

phrases = { r"gra[scz]i(a[sz']?|ela)": r"no, \0 a vo'",
            r"thank(s| you)": r"no, thank you"}
phrases = [(re.compile(key),phrases[key]) for key in phrases]

# Main loop

subredditsStr = config["something"]["subreddits"].replace(",","+")
refreshTime = config["praw"]["refresh_time"]
processed = set()
lastScantime = time.time()

system.exit(0)

while True:
    try:
        previousScantime = lastScantime
        lastScantime = time.time()

        subreddits = reddit.get_subreddit(subredditsStr)
        comments = praw.helpers.flatten_tree(subreddits.get_comments())

        count = 0

        for comment in comments:
            count += 1

            if comment["id"] not in processed:
                processed.add(comment["id"])

                if float(comment["created_utc"]) > previousScantime:
                    text = comment["selftext"]
                    user = comment["author"]["user_name"]

                    for (regex,reply) in phrases:
                        match = regex.search(text, re.IGNORECASE)

                        if match:
                            reply = match.expand(reply)
                            comment.reply(reply)

                            log("Replied \"" + reply + " to a " + user + "'s comment,"
                                "URL: " + comment.permalink)
                            break

        log("Scanned " + str(count) + " comments")

        time.sleep(refreshTime)

    except:
        pass

