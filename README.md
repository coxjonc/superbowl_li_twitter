Pull time-stamped tweets from the Twitter Streaming API and load them into a MySQL database
===

Installation and Environment config
---
Navigate to the root directory of the project and run the following to install python dependencies. It's recommended that you install with a virtualenv:

`pip install -r requirements.txt`

Set the following environmental variables:

* `DATABASE_URL`: The full URL of your MySQL database `mysql://<username>:<password>@<host>:<port>/<db_name>`

* `TWITTER_ACCESS_TOKEN`, `TWITTER_ACCESS_SECRET`, `TWITTER_KEY`, and `TWITTER_SECRET`. Parsing Twitter requires an API key and access token. Create a Twitter application at [apps.twitter.com](https://apps.twitter.com/), get your API keys and access tokens, and add them to the following environmental variables

A tool like `virtualenvwrapper` will allow you to automatically export these environmental variables every time the virtualenv is activated, to save you the trouble of typing them out every time.

Load tweets into database
---
Once you have your environment configured and have installed all the necessary packages, run the script to import tweets from the [Twitter API's stream](https://dev.twitter.com/streaming/overview) into your MySQL DB. Run with `nohup` if you want Unix to ignore the hangup (HUP) signal

The python script can also be wrapped in a shell script that restarts after being unexpectedly terminated.

`nohup ./bin/forever.sh`

To keep tabs on the logs just run `tail -f ./bin/nohup.out`.

The script saves data about whether the tweet contains key terms associated with the Atlanta Falcons or New England Patriots, but can be easily configured to look for other key terms.


Write tweet data to S3
---
If you want to upload tweet data live to S3, copy `./bin/write_tweets_s3.sh` into your scripts directory, run `chmod +x write_tweets_s3` to give it execute permission, and set up a cron job to run the script automatically. To run a cron job that would update the CSV on S3 every 5 minutes, for instance, you would type `crontab -e` and add the following add:

`*/5 * * * * /path/to/your/script`

That's all there is to it! Usually if there are errors cron will output a log to /var/mail/your-username, so check there to make sure the script is working properly.

Development
---
The code for pulling the tweets from the Twitter Streaming API and writing to S3 lives in `bin`. Frontend code lives in `web`.

