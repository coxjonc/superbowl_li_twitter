Pull time-stamped tweets about the Falcons and Patriots from the Twitter API
===

Installation and Environment config
---
`pip install -r requirements.txt`

Set the following environmental variables:

`DATABASE_URL`: The full URL of your MySQL database `mysql://<username>:<password>@<host>:<port>/<db_name>`

Parsing Twitter requires an API key and access token. Create a Twitter application at [apps.twitter.com](https://apps.twitter.com/), get your API keys and access tokens, and add them to the following environmental variables

`TWITTER_ACCESS_TOKEN`, `TWITTER_ACCESS_SECRET`, `TWITTER_KEY`, and `TWITTER_SECRET`


Load tweets into database
---
Once you have your environment configured and have installed all the necessary packages, run the script to import tweets from the livestream into your MySQL DB. Run with `nohup` if you want Unix to ignore the hangup (HUP) signal

`nohup python bin/stream_to_sql.py&`
