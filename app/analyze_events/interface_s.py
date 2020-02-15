import re
import threading
from datetime import timedelta, datetime

import tweepy

from app.analyze_events import algorithm_s
from app.utility import utility

GROUP_TIME_UNIT = 1140  # minutes (1 day)


def analyze_events(data):
    res = {}
    # threads
    threads = []
    now = datetime.now() + timedelta(days=1)
    for day_index in range(0, 10):
        crr_date = now - timedelta(days=day_index)
        t = threading.Thread(name="search_topic_" + str(day_index), target=worker_1, args=(crr_date, res, data))
        t.start()
        threads.append(t)

    for thread in threads:
        # join threads
        thread.join()

    # process tweets
    all_tweets = {}
    for key in res:
        for tweet in res[key]:
            if tweet.id_str not in all_tweets:
                # tweet not found
                all_tweets[tweet.id_str] = tweet
            # check on re-tweet
            if hasattr(tweet, 'retweeted_status'):
                if tweet.retweeted_status.id_str not in all_tweets:
                    # tweet not found
                    all_tweets[tweet.retweeted_status.id_str] = tweet.retweeted_status

    # make tweet time line
    tweet_timeseries = dict()
    for key in all_tweets:
        timestamp = all_tweets[key].created_at.timestamp()
        if timestamp not in tweet_timeseries:
            tweet_timeseries[timestamp] = []
        tweet_timeseries[int(timestamp)].append(key)

    grouped_time_series = dict()
    pre_time = 0
    # get all time stamp keys
    for timestamp in sorted(tweet_timeseries.keys()):
        date_diff = now - datetime.fromtimestamp(timestamp)
        if date_diff.days < 31:
            if pre_time == 0:
                pre_time = timestamp
            if int(round((timestamp - pre_time) / 60)) >= GROUP_TIME_UNIT:
                grouped_time_series[timestamp] = tweet_timeseries.get(timestamp)
                pre_time = timestamp
            else:
                if pre_time not in grouped_time_series:
                    grouped_time_series[pre_time] = []
                for time_val in tweet_timeseries.get(timestamp):
                    grouped_time_series[pre_time].append(time_val)

    # analyze tweet data
    algorithm = algorithm_s.EventAnalyser()
    forecast = algorithm.analyze_event(grouped_time_series)
    clustered_words = algorithm.analyze_text(all_tweets)

    response = {
        'time_series': grouped_time_series,
        'forecast': forecast,
        'clustered_words': clustered_words
    }

    return response


def worker_1(day, res, data):
    since_date = day - timedelta(days=1)
    tweets = []
    api, conn_key = utility.create_api_connection()
    for tweet in tweepy.Cursor(api.search, q=data['topic'], since=since_date.strftime('%Y-%m-%d'),
                               until=day.strftime('%Y-%m-%d'), lang="en").items(data['count']):
        tweets.append(tweet)

    # close connection
    utility.close_connection(conn_key)
    # add to main list
    res[since_date.strftime('%Y-%m-%d')] = tweets


def find_users(data):
    api, conn_key = utility.create_api_connection()
    res = []
    users = api.search_users(q=data['user'])
    for user in users:
        res.append(user._json)

    # close connection
    utility.close_connection(conn_key)
    return res


def analyse_user_profile(data):
    res = {
        'recent_tweets': [],
        'hash_tags': {}
    }

    api, conn_key = utility.create_api_connection()
    tweets = api.user_timeline(id=data['id'])
    for tweet in tweets:
        res['recent_tweets'].append(tweet._json)
        # get hash tags filtered
        hash_tags = re.findall(r"#(\w+)", tweet.text)
        for tag in hash_tags:
            if tag not in res['hash_tags']:
                res['hash_tags'][tag] = 0
            res['hash_tags'][tag] += 1

    return res
