from flask import Flask, jsonify, send_file, request
from flask_cors import CORS

from app.analyze_events import interface_s
from app.analyze_retweet import interface_h
from app.analyze_retweet.re_tweet_geo_location import re_tweet_geo_location
from app.analyze_tweets import interface_k
from app.analyze_tweets.tweet_geo_location import tweet_geo_location
from app.time_analysis import interface_c

app = Flask(__name__)
cors = CORS(app, resources={"/api/*": {"origins": "*"}})


# ----------------------------------------------------------------------------------------------------------------------
# Default - launch index.html
# ----------------------------------------------------------------------------------------------------------------------

@app.route("/")
def root():
    return send_file("static/index.html")


# ----------------------------------------------------------------------------------------------------------------------
# API - Routing
# ----------------------------------------------------------------------------------------------------------------------

@app.route("/api/analyzeTweet", methods=['POST'])
def get_data():
    res = interface_k.analyze_tweets(request.json)
    return jsonify(res)


@app.route("/api/compareTopics", methods=['POST'])
def get_cluster():
    res = interface_c.compare_topics(request.json)
    return jsonify(res)


@app.route("/api/analyzeEvent", methods=['POST'])
def get_analyze_event():
    res = interface_s.analyze_events(request.json)
    return jsonify(res)


@app.route("/api/analyzeRetweet", methods=['POST'])
def get_analyze_retweet():
    res = interface_h.analyze_retweet(request.json)
    return jsonify(res)


@app.route("/api/retweetGeoCoordinates", methods=['POST'])
def get_re_tweet_geo_coordinates():
    # get geo locations for tweeted users
    geo = re_tweet_geo_location()
    geo.find_locations(request.json)
    res = geo.get_locations()
    return jsonify(res)


@app.route("/api/getUsers", methods=['POST'])
def get_users():
    # get users for given text
    users = interface_s.find_users(request.json)
    return jsonify(users)


@app.route("/api/analyseUserProfile", methods=['POST'])
def analyse_user_profile():
    # analyze user profile
    res = interface_s.analyse_user_profile(request.json)
    return jsonify(res)


@app.route("/api/analyzeFalseTweets", methods=['POST'])
def analyze_false_tweets():
    # analyze user profile
    res = interface_k.analyze_false_tweets(request.json)
    return jsonify(res)


@app.route("/api/tweetGeoCoordinates", methods=['POST'])
def get_tweet_geo_coordinates():
    # get geo locations for tweeted users
    geo = tweet_geo_location()
    geo.find_locations(request.json)
    res = geo.get_locations()
    return jsonify(res)


if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=int(6699)
    )
