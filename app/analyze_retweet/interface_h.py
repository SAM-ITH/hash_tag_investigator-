import datetime
import json
import threading

import tweepy

from app.analyze_retweet import algorithm_h
from app.analyze_retweet.predictions_h import predictions_h
from app.utility import utility


def dump_output(data):
    f = open('output.json', 'w')
    f.write(json.dumps(data))
    f.close()


def create_predicting_values(type, gap, steps, last_timestamp):
    pred_list = []
    delta = 0
    for i in range(1, steps):
        delta += i * gap
        if type is "S":
            pred_list.append(last_timestamp + datetime.timedelta(seconds=delta).total_seconds())
        elif type is "M":
            pred_list.append(last_timestamp + datetime.timedelta(minutes=delta).total_seconds())
        elif type is "H":
            pred_list.append(last_timestamp + datetime.timedelta(hours=delta).total_seconds())

    return pred_list


def analyze_retweet(data):
    # response
    res = {
        'topic_1': {},
        'topic_2': {}
    }
    threads = []
    for topic_index in range(1, 3):
        # ----- search topic -----
        t = threading.Thread(name="search_" + str(topic_index), target=worker, args=(data, res, topic_index))
        t.start()
        threads.append(t)

    threads[0].join()
    threads[1].join()

    return res


def worker(data, res, topic_index):
    # main list
    main_list = dict()
    # holds API connection
    api, conn_key = utility.create_api_connection()
    for tweet in tweepy.Cursor(api.search, q=data['topic_' + str(topic_index)], result_type="recent",
                               include_entities=True,
                               lang="en").items(data['count']):
        # define temp tweet
        parsed_tweet = {}
        # parse id
        parsed_tweet['id'] = tweet.id
        # parse coordinates
        parsed_tweet['coordinates'] = tweet.coordinates
        # parse user location
        parsed_tweet['user_location'] = tweet.user.location
        # parse geo
        parsed_tweet['geo'] = tweet.geo
        # created_at
        parsed_tweet['created_at'] = tweet.created_at
        # user profile image url
        parsed_tweet['profile_image_url'] = tweet.user.profile_image_url
        # parse tweet text
        parsed_tweet['text'] = tweet.text

        # pass to main data list
        if tweet.created_at.timestamp() not in main_list:
            main_list[tweet.created_at.timestamp()] = []
        main_list[tweet.created_at.timestamp()].append({
            'id': tweet.id,
            'tweet': tweet._json
        })

    # close connection
    utility.close_connection(conn_key)

    # dump_output(main_list)
    algorithm = algorithm_h.AnalyzeRetweets()
    algorithm.process_tweets(main_list)
    # predictions
    time_series = [int(i) for i in algorithm.get_tweet_timeline().keys()]
    predicting_timeline = create_predicting_values("M", 5, 31, time_series[len(time_series) - 1])

    # for -> tweets
    tweets_model = predictions_h()
    tweets_model.make_model(
        time_series,
        list(algorithm.get_tweet_timeline().values())
    )
    # pass predicting timestamp values
    tweets_predictions = tweets_model.make_predictions(predicting_timeline)

    # for -> re_tweets
    re_tweets_model = predictions_h()
    re_tweets_model.make_model(
        time_series,
        list(algorithm.get_re_tweet_timeline().values())
    )
    # pass predicting timestamp values
    re_tweets_predictions = re_tweets_model.make_predictions(predicting_timeline)

    # for -> likes
    likes_model = predictions_h()
    likes_model.make_model(
        time_series,
        list(algorithm.get_likes_timeline().values())
    )
    # pass predicting timestamp values
    likes_predictions = likes_model.make_predictions(predicting_timeline)

    # for -> followers
    followers_model = predictions_h()
    followers_model.make_model(
        time_series,
        list(algorithm.get_followers_timeline().values())
    )
    # pass predicting timestamp values
    followers_predictions = followers_model.make_predictions(predicting_timeline)

    # for -> comments
    comments_model = predictions_h()
    comments_model.make_model(
        time_series,
        list(algorithm.get_comments_timeline().values())
    )
    # pass predicting timestamp values
    comments_predictions = comments_model.make_predictions(predicting_timeline)

    temp = {
        'tweet_count': algorithm.get_tweet_count(),
        'tweet_timeline': algorithm.get_tweet_timeline(),
        're_tweet_count': algorithm.get_re_tweet_count(),
        're_tweet_timeline': algorithm.get_re_tweet_timeline(),
        'followers_count': algorithm.get_followers_count(),
        'followers_timeline': algorithm.get_followers_timeline(),
        'comments_count': algorithm.get_comments_count(),
        'comments_timeline': algorithm.get_comments_timeline(),
        'likes_count': algorithm.get_likes_count(),
        'likes_timeline': algorithm.get_likes_timeline(),
        'predicting_timeline': predicting_timeline,
        'tweets_predictions': [i[0] for i in tweets_predictions.tolist()],
        're_tweets_predictions': [i[0] for i in re_tweets_predictions.tolist()],
        'likes_predictions': [i[0] for i in likes_predictions.tolist()],
        'followers_predictions': [i[0] for i in followers_predictions.tolist()],
        'comments_predictions': [i[0] for i in comments_predictions.tolist()],
        'users': algorithm.get_users()
    }
    res['topic_' + str(topic_index)] = temp
