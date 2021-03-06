import praw
import time
import configparser
import os.path
import sys
import re
import requests

log = lambda s : print(time.strftime("%Y-%m-%d %H:%M:%S")+": "+str(s))

# Set the working directory as the script's own directory

os.chdir(os.path.dirname(sys.argv[0]))

# Configuration

configName = "../config.cfg"
config = configparser.ConfigParser()
config["credentials"] = {"username": "",
                         "password": ""}
config["something"] = {"subreddits": "",
                       "userignore": ""} # Comma delimited
config["praw"] = {"refresh_time": "5.0"}

if os.path.isfile(configName):
    config.read(configName)
else:
    with open(configName, "w") as configFile:
        config.write(configFile)

if not config["credentials"]["username"] or not config["credentials"]["password"]:
    log("Set an username and password in "+configName)
    sys.exit(1)

if not config["something"]["subreddits"]:
    log("Specify some subreddits in "+configName)
    sys.exit(2)

if float(config["praw"]["refresh_time"]) < 2.0:
    log("The refresh time is too short, using 2 seconds")
    config["praw"]["refresh_time"] = "2.0"

# Connect to reddit

username = config["credentials"]["username"]
password = config["credentials"]["password"]

reddit = praw.Reddit("grasiabot"
                     "Url:github.com/ABorgna/graciaabot")
reddit.login(username=username,password=password)

log("Logged in as "+username)

# Beware of the regular expressions

phrases = { r"(gra[scz]i(a|ela))[sz']?": r"no, grasi\2 a vo'",
            r"thank(s| you)": r"no, thank you"}
phrases = [(re.compile(key,re.I),phrases[key]) for key in phrases]

# Main loop

subredditsStr = config["something"]["subreddits"].replace(",","+")
ignoredUsers = [x.lower() for x in config["something"]["userignore"].split(",")]
refreshTime = float(config["praw"]["refresh_time"])
processed = set()
replyQueue = []
startTimestamp = time.time()

log("Scanning subreddits "+subredditsStr)

while True:
    try:
        subreddits = reddit.get_subreddit(subredditsStr)
        comments = subreddits.get_comments()

        count = 0

        for comment in comments:
            if comment.id not in processed and float(comment.created_utc) > startTimestamp:
                count += 1
                processed.add(comment.id)

                text = comment.body
                user = comment.author.name.lower()

                if user == username.lower():
                    continue
                elif user in ignoredUsers:
                    reply = "e gato ke habla"
                    replyQueue.insert(0,(comment,reply))
                else:
                    for (regex,reply) in phrases:
                        match = regex.search(text)

                        if match:
                            reply = match.expand(reply).lower()
                            replyQueue.insert(0,(comment,reply))
                            break

        log("Scanned " + str(count) + " comments")

        while replyQueue:
            comment, reply = replyQueue[-1]
            comment.reply(reply)
            replyQueue.pop()

            user = comment.author.name
            log("Replied \"" + reply + "\" to a " + user + "'s comment,"
                "URL: " + comment.permalink)

        time.sleep(refreshTime)

    except KeyboardInterrupt:
        log("Stopped by user")
        sys.exit(0)
    except praw.errors.APIException as e:
        log("ApiException, %s, sleeping five minutes" %e)
        time.sleep(5*60)
    except praw.errors.ClientException as e:
        log("ClientException, %s, reconnecting and sleeping one minute" %e)
        time.sleep(60)
        reddit.login(username=username,password=password)
    except praw.errors.InvalidCaptcha:
        log("InvalidCaptcha, waiting five minutes")
        time.sleep(5*60)
    except praw.errors.InvalidComment as e:
        log("InvalidComment, %s, retrying" %e)
        pass
    except praw.errors.InvalidSubreddit as e:
        log("InvalidSubreddit, %s, quitting" %e)
        sys.exit(1)
    except praw.errors.LoginRequired:
        log("LoginRequired, reconnecting")
        reddit.login(username=username,password=password)
    except praw.errors.NotLoggedIn:
        log("NotLoggedIn, reconnecting")
        reddit.login(username=username,password=password)
    except praw.errors.RateLimitExceeded:
        log("RateLimitExceeded, we are commenting to much. Waiting two minutes")
        time.sleep(2*60)
    except requests.exceptions.HTTPError as e:
        log("HTTPError, %s, waiting a minute" % e)
        time.sleep(60)

