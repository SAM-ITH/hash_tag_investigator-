from datetime import datetime, timedelta

import tweepy

from app.analyze_tweets import algorithm_k
from app.utility import utility


# exposed method to analyze tweets
def analyze_tweets(data):
    # classifier
    classifier = algorithm_k.Classifire()
    # response
    res = {}
    # tweets list
    tweets = []
    # sentiments counts
    positive_c = 0
    negative_c = 0
    neutral_c = 0
    # holds API connection
    api, conn_key = utility.create_api_connection()
    for tweet in tweepy.Cursor(api.search, q=data['text'], result_type="recent", include_entities=True,
                               lang="en").items(data['count']):
        # define temp tweet
        parsed_tweet = {}
        # parse id
        parsed_tweet['id'] = tweet.id
        # parse coordinates
        parsed_tweet['coordinates'] = tweet.coordinates
        # parse user
        parsed_tweet['user'] = tweet.user._json
        parsed_tweet['user']['created_at'] = tweet.user.created_at.timestamp()  # convert datetime to timestamp
        # parse geo
        parsed_tweet['geo'] = tweet.geo
        # created_at
        parsed_tweet['created_at'] = tweet.created_at
        # user profile image url
        parsed_tweet['profile_image_url'] = tweet.user.profile_image_url
        # parse tweet text
        parsed_tweet['text'] = tweet.text
        # sentiment
        parsed_tweet['sentiment'] = classifier.naive_bayes_sentiment_calculator(tweet.text)
        # append to main tweets
        tweets.append(parsed_tweet)

        # update counts
        if parsed_tweet['sentiment'] == 'positive':
            positive_c += 1
        elif parsed_tweet['sentiment'] == 'neutral':
            neutral_c += 1
        else:
            negative_c += 1

    # close connection
    utility.close_connection(conn_key)

    res['tweets'] = tweets
    res['positive_count'] = positive_c
    res['neutral_count'] = neutral_c
    res['negative_count'] = negative_c

    return res


# ratings for fake identification
FAKE_DATE = 0.40
FAKE_BIO = 0.10
FAKE_FOLLOWING = 0.25
FAKE_TWEETS_COUNT = 0.20
FAKE_FOLLOWERS_COUNT = 0.05

MAX_TWEETS = 100000


def analyze_false_tweets(tweets):
    fake_tweets = []
    real_tweets = []
    fake_users = []
    now = datetime.now()  # get current datetime
    for tweet in tweets['tweets']:
        profile_rating = 1.0  # keep rating for track fakeness of the profile
        user = tweet['user']  # get tweeted user
        # filter user with set of rules and identify according to their ranking
        # whether fake or real user
        # 1. check, already user found as fake one on the list
        if user['id'] not in fake_users:
            # ----- Apply Rules -----
            # 1. check profile created at date
            created_at = datetime.fromtimestamp(int(user['created_at']))
            if now - timedelta(hours=24) <= created_at <= now:
                # account created within last 24 hours
                profile_rating -= FAKE_DATE
            # 2. check for empty bio
            if not is_not_empty(user['description']):
                # empty bio found
                profile_rating -= FAKE_BIO
            # 3. check following count is 2001 or not
            if int(user['friends_count']) == 2001:
                # many fake accounts get stuck on following 2,001 users
                profile_rating -= FAKE_FOLLOWING
            # 4. check tweets count
            if int(user['statuses_count']) > MAX_TWEETS:
                # Insane amount of tweets
                profile_rating -= FAKE_TWEETS_COUNT
            # 5. check followers
            if int(user['followers_count']) < 10:
                # low followers number or no followers at all
                profile_rating -= FAKE_FOLLOWERS_COUNT

            # check profile rating
            if profile_rating > 0.60:
                # good profile
                real_tweets.append(tweet)
            else:
                fake_users.append(user['id'])
                fake_tweets.append(tweet)
        else:
            fake_users.append(user['id'])
            fake_tweets.append(tweet)

    res = {
        'real': real_tweets,
        'fake': fake_tweets
    }
    return res


def is_not_empty(s):
    return bool(s and s.strip())
