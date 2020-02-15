# common count
import threading

import tweepy

from app.analyze_tweets import algorithm_k
from app.utility import utility

common_count = 5

GROUP_TIME_UNIT = 20  # minutes


def compare_topics(data):
    res = {}
    threads = []  # holds all threads
    for topic_index in range(1, 3):
        # go through topics
        # check on selected categories
        index = 1  # category ID
        for category in data['categories']:
            if category['status']:
                t = threading.Thread(name="search_" + str(topic_index) + "_" + str(index), target=worker_1,
                                     args=(data, res, topic_index, category['title'], index))
                t.start()
                threads.append(t)
            index += 1

    for thread in threads:
        # join threads
        thread.join()

    # clear threads
    threads.clear()

    grouped_topics = {
        'topic_1': dict(),
        'topic_1_total': 0,
        'topic_1_positive': 0,
        'topic_1_negative': 0,
        'topic_1_neutral': 0,
        'topic_2': dict(),
        'topic_2_total': 0,
        'topic_2_positive': 0,
        'topic_2_negative': 0,
        'topic_2_neutral': 0
    }
    # build main time line
    for topic in range(1, 3):
        t = threading.Thread(name="make_time_series_" + str(topic), target=worker_2,
                             args=(data, res, grouped_topics, topic))
        t.start()
        threads.append(t)

    for thread in threads:
        # join threads
        thread.join()

    return grouped_topics


def worker_1(data, res, topic_index, category, category_id):
    # classifier
    classifier = algorithm_k.Classifire()
    # main list
    main_list = dict()
    # holds categories data
    main_list_category = dict()
    # create empty list
    res['topic_' + str(topic_index) + "_" + str(category_id)] = []
    # holds API connection
    api, conn_key = utility.create_api_connection()
    for tweet in tweepy.Cursor(api.search, q=data['topic_' + str(topic_index)] + " " + category, result_type="recent",
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
        # sentiment
        parsed_tweet['sentiment'] = classifier.naive_bayes_sentiment_calculator(tweet.text)
        # append to main list
        # pass to main data list
        if tweet.created_at.timestamp() not in main_list:
            main_list[tweet.created_at.timestamp()] = []
            main_list_category[tweet.created_at.timestamp()] = 0
        main_list[tweet.created_at.timestamp()].append(parsed_tweet)
        main_list_category[tweet.created_at.timestamp()] += 1

    # close connection
    utility.close_connection(conn_key)

    count_timeline = {}

    # build individual time lines
    for timestamp in sorted(main_list):
        # read tweets for timestamp group
        pos_count = 0
        neg_count = 0
        neu_count = 0
        for tweet in main_list[timestamp]:
            if tweet['sentiment'] == "positive":
                pos_count += 1
            elif tweet['sentiment'] == "negative":
                neg_count += 1
            elif tweet['sentiment'] == "neutral":
                neu_count += 1

        count_timeline = update_topic(pos_count, neg_count, neu_count, timestamp, count_timeline)

    # update main list
    res['topic_' + str(topic_index) + "_" + str(category_id)] = count_timeline
    res['topic_' + str(topic_index) + "_" + str(category_id) + "_tweet_count"] = main_list_category


def worker_2(data, res, grouped_topics, topic):
    time_series = dict()
    index = 1  # category ID
    for category in data['categories']:
        if category['status']:
            for timestamp in res['topic_' + str(topic) + "_" + str(index)].keys():
                if timestamp not in time_series:
                    time_series[timestamp] = {
                        'positive': 0,
                        'negative': 0,
                        'neutral': 0
                    }
                # get percentage value
                time_series[timestamp]['positive'] += res['topic_' + str(topic) + "_" + str(index)][timestamp][
                    'positive']
                time_series[timestamp]['negative'] += res['topic_' + str(topic) + "_" + str(index)][timestamp][
                    'negative']
                time_series[timestamp]['neutral'] += res['topic_' + str(topic) + "_" + str(index)][timestamp][
                    'neutral']
        index += 1

    grouped_time_series = dict()
    pre_time = 0
    # get all time stamp keys
    for timestamp in sorted(time_series.keys()):
        if pre_time == 0:
            pre_time = timestamp
        if int(round((timestamp - pre_time) / 60)) >= GROUP_TIME_UNIT:
            grouped_time_series[timestamp] = {
                'positive': time_series[timestamp]['positive'],
                'negative': time_series[timestamp]['negative'],
                'neutral': time_series[timestamp]['neutral']
            }
            pre_time = timestamp
        else:
            if pre_time not in grouped_time_series:
                grouped_time_series[pre_time] = {
                    'positive': 0,
                    'negative': 0,
                    'neutral': 0
                }

            grouped_time_series[pre_time]['positive'] += time_series[timestamp]['positive']
            grouped_time_series[pre_time]['negative'] += time_series[timestamp]['negative']
            grouped_time_series[pre_time]['neutral'] += time_series[timestamp]['neutral']

        grouped_topics['topic_' + str(topic) + "_positive"] += time_series[timestamp]['positive']
        grouped_topics['topic_' + str(topic) + "_negative"] += time_series[timestamp]['negative']
        grouped_topics['topic_' + str(topic) + "_neutral"] += time_series[timestamp]['neutral']
        grouped_topics['topic_' + str(topic) + "_total"] += 1

    # get all time stamp keys
    main_grouped_time_series = {}
    index = 1
    for category in data['categories']:
        if category['status']:
            pre_time = 0
            grouped_time_series_2 = dict()
            for timestamp in sorted(time_series.keys()):
                if pre_time == 0:
                    pre_time = timestamp
                if int(round((timestamp - pre_time) / 60)) >= GROUP_TIME_UNIT:
                    # set category tweet counting
                    if timestamp in res['topic_' + str(topic) + "_" + str(index) + "_tweet_count"]:
                        grouped_time_series_2[timestamp] = \
                            res['topic_' + str(topic) + "_" + str(index) + "_tweet_count"][timestamp]
                    else:
                        grouped_time_series_2[timestamp] = 0
                    pre_time = timestamp
                else:
                    if pre_time not in grouped_time_series_2:
                        # set category tweet counting
                        grouped_time_series_2[pre_time] = 0

                    # set category tweet counting
                    if timestamp in res['topic_' + str(topic) + "_" + str(index) + "_tweet_count"]:
                        grouped_time_series_2[pre_time] += \
                            res['topic_' + str(topic) + "_" + str(index) + "_tweet_count"][timestamp]
            main_grouped_time_series[category['title']] = grouped_time_series_2
        index += 1

    # update main list
    grouped_topics['topic_' + str(topic)] = grouped_time_series
    # update main list with category tweet counting
    grouped_topics['topic_' + str(topic) + "_tweet_count"] = main_grouped_time_series


def update_topic(pos_count, neg_count, neu_count, timestamp, items):
    if timestamp not in items:
        items[timestamp] = {}
    items[timestamp] = {
        'positive': pos_count,
        'negative': neg_count,
        'neutral': neu_count
    }
    return items
