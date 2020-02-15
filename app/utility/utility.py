import random
from random import randrange

import tweepy

from app.utility import tweeter_configs as config

# holds current connection pool
connection_pool = []


# crete API connection with Tweeter
def create_api_connection():
    # get connection pool key
    key = get_key_id()
    consumer_key = config.keys['consumer_key_' + str(key)]
    consumer_secret = config.keys['consumer_secret_' + str(key)]
    access_token = config.keys['access_token_' + str(key)]
    access_token_secret = config.keys['access_token_secret_' + str(key)]

    # connect with tweeter API
    auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
    auth.set_access_token(access_token, access_token_secret)
    api = tweepy.API(auth)
    return api, key


# get free connection ID
def get_key_id():
    key = 0  # default key
    if connection_pool.__len__() == 0:
        # no connection found
        key = randrange(1, config.auth_key_count)
    else:
        # connections found on pool
        temp = []
        for i in range(1, config.auth_key_count + 1):
            found = False
            for x in connection_pool:
                if x == i:
                    found = True
                    break
            if not found:
                temp.append(i)
        # free user account found
        key = random.choice(temp)

    # update connection pool
    connection_pool.append(key)
    print("Create : ", key)
    return key


# remove key from connection pool
def close_connection(key):
    print("Close : ", key)
    connection_pool.remove(key)
