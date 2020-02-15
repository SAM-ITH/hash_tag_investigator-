import string
from collections import Counter

from nltk import pos_tag
from nltk.corpus import stopwords

from app.analyze_events import utility_functions

# hold punctuations
punctuations = list(string.punctuation)
# holds stopwords
stops = set(stopwords.words("english"))


class CompareTopics(object):
    # filter only positive tweets
    def filter_positive(self, topic_results):
        positive_tweets_set = []
        for tweet in topic_results:
            if tweet['sentiment'] == 'positive':
                positive_tweets_set.append(tweet)
        return positive_tweets_set

    # compare tweets
    def compare_tweets(self, tweet_set):
        # holds word counter
        word_counter = Counter()
        # process set 1
        for tweet in tweet_set:
            # create tokenizer set 1
            tweet_set_tokens = utility_functions.pre_process(tweet['text'])
            # remove stopwords (common words)
            filtered_words = [word for word in tweet_set_tokens if word not in stops]
            # remove punctuations from token
            filtered_words = [i for i in filtered_words if i not in punctuations]
            # filter only nouns
            filtered_words = self.get_nouns(filtered_words)
            # update word counter
            word_counter.update(filtered_words)
        return word_counter

    def get_nouns(self, tokens):
        nouns = [token for token, pos in pos_tag(tokens) if pos.startswith('N')]
        return nouns
