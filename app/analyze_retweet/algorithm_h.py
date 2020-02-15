class AnalyzeRetweets(object):
    def __init__(self):
        # entity variables
        self._followers_count = 0
        self._tweet_count = 0
        self._re_tweet_count = 0
        self._comments_count = 0
        self._likes_count = 0
        # holds followers for date times, on tweets created
        self._followers_timeline = {}
        self._tweet_timeline = {}
        self._re_tweet_timeline = {}
        self._comments_timeline = {}
        self._likes_timeline = {}
        self._users = []

    # check for re tweeted tweet
    def is_re_tweet(self, tweet):
        status = False
        if 'retweeted_status' in tweet:
            status = True
        if tweet['retweeted']:
            status = True
        return status

    # check for comment tweet
    def is_comment(self, tweet):
        if tweet['in_reply_to_status_id']:
            return True
        return False

    # update followers timeline
    def update_followers(self, key):
        if key not in self._followers_timeline:
            self._followers_timeline[key] = 0
        self._followers_timeline[key] = self._followers_count

    # update like timeline
    def update_likes(self, key):
        if key not in self._likes_timeline:
            self._likes_timeline[key] = 0
        self._likes_timeline[key] = self._likes_count

    # update re tweet timeline
    def update_re_tweets(self, key):
        if key not in self._re_tweet_timeline:
            self._re_tweet_timeline[key] = 0
        self._re_tweet_timeline[key] = self._re_tweet_count

    # update comment tweet timeline
    def update_comment_tweets(self, key):
        if key not in self._comments_timeline:
            self._comments_timeline[key] = 0
        self._comments_timeline[key] = self._comments_count

    # update main tweet timeline
    def update_org_tweets(self, key):
        if key not in self._tweet_timeline:
            self._tweet_timeline[key] = 0
        self._tweet_timeline[key] = self._tweet_count

    def process_tweets(self, data):
        # sort by timestamp
        for timestamp in sorted(data):
            # tweets for specific timestamp (can be one or more tweets)
            for value in data[timestamp]:
                state = "tweet"
                # check for re-tweet
                if self.is_re_tweet(value['tweet']):
                    state = "re_tweet"
                    self._re_tweet_count += 1
                elif self.is_comment(value['tweet']):
                    state = "comment"
                    self._comments_count += 1
                else:
                    # original tweet found
                    self._tweet_count += 1

                # update likes
                self._likes_count += value['tweet']['favorite_count']
                self.update_likes(timestamp)

                # update followers (do at end)
                self._followers_count += 1
                self.update_followers(timestamp)

                # update re tweets
                self.update_re_tweets(timestamp)
                # update comments
                self.update_comment_tweets(timestamp)
                # update org tweet
                self.update_org_tweets(timestamp)

                # update users
                self._users.append({'type': state, 'user': value['tweet']['user']})

    def get_tweet_count(self):
        return self._tweet_count

    def get_tweet_timeline(self):
        return self._tweet_timeline

    def get_re_tweet_count(self):
        return self._re_tweet_count

    def get_re_tweet_timeline(self):
        return self._re_tweet_timeline

    def get_followers_count(self):
        return self._followers_count

    def get_followers_timeline(self):
        return self._followers_timeline

    def get_comments_count(self):
        return self._comments_count

    def get_comments_timeline(self):
        return self._comments_timeline

    def get_likes_count(self):
        return self._likes_count

    def get_likes_timeline(self):
        return self._likes_timeline

    def get_users(self):
        return self._users
