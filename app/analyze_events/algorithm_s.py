import os
import re
# holds directory path
import string
from datetime import datetime, timedelta

import nltk
import numpy as np
from nltk.corpus import stopwords
from nltk.tokenize.casual import TweetTokenizer
from pandas.io.parsers import read_csv
from statsmodels.tsa.arima_model import ARIMA

import app.analyze_events.utility_functions as utility

dir_path = os.path.dirname(os.path.realpath(__file__))

# set not of predicting day count
predict_day_count = 7

# function to test noun
is_noun = lambda pos: pos[:2] == 'NN'


class EventAnalyser(object):
    # group data by date
    grouped_data = dict()
    # main tweet count arr
    tweet_count_set = []

    def __init__(self):
        self._cache_english_stopwords = stopwords.words('english')
        self._prediction = []
        self._training_data = {}

    def analyze_event(self, data_set):
        col_1_list = []  # column 1
        col_2_list = []  # column 2

        # pre-process data
        for timestamp in data_set.keys():
            if timestamp not in self._training_data:
                self._training_data[timestamp] = 0
            self._training_data[timestamp] += len(data_set.get(timestamp))

            col_1_list.append(datetime.fromtimestamp(int(timestamp)).strftime("%Y-%m-%d"))
            col_2_list.append(float(self._training_data[timestamp]))

        # save to CSV for make predictions, also to backup last predicting data set
        path = '/workspace/hash-tag-investor/app/dataset/prediction.csv'
        np.savetxt(path,
                   np.column_stack((col_1_list, col_2_list)),
                   delimiter=',',
                   header="date,count",
                   fmt='%s')

        # read parsed data from CSV
        series = read_csv(path, header=0, parse_dates=[0], index_col=0,
                          squeeze=True)
        # make ARIMA model
        models = []
        aic = []
        count = 0
        for p in range(0, 5):
            for d in range(0, 2):
                for q in range(0, 5):
                    try:
                        model = ARIMA(series, order=(p, d, q)).fit(disp=0)
                        models.append(model)
                        aic.append({
                            'id': count,
                            'aic': model.aic
                        })
                        count += 1
                    except Exception as e:
                        pass

        forecast_data = {}
        if len(aic) > 0:
            pre_aic = -9999
            pre_id = 0
            for aic_obj in aic:
                if pre_aic == -9999:
                    pre_aic = aic_obj['aic']
                    pre_id = aic_obj['id']
                if pre_aic > aic_obj['aic']:
                    # lower AIC value found
                    pre_aic = aic_obj['aic']
                    pre_id = aic_obj['id']

            forecast = models[pre_id].forecast(steps=predict_day_count, exog=None, alpha=0.95)
            print(forecast[0])
            # forecasting results
            now = datetime.now()
            for i in range(1, predict_day_count + 1):
                day = now + timedelta(days=i)
                forecast_data[day.timestamp()] = forecast[0][(i-1)]

        return forecast_data

    def analyze_text(self, data):
        word_list = {}
        for tweet_id in data:
            tokenize_tweet = nltk.word_tokenize(utility.pre_process(data[tweet_id].text))
            nouns = [word for (word, pos) in nltk.pos_tag(tokenize_tweet) if is_noun(pos)]
            # check on nouns
            for word in nouns:
                if word not in word_list:
                    word_list[word] = 0
                word_list[word] += 1

        temp = dict()
        for key in word_list:
            if word_list[key] not in temp:
                temp[word_list[key]] = []
            temp[word_list[key]].append(key)

        return temp

    def tweet_clean(self, tweet):
        # Remove tickers
        sent_no_tickers = re.sub(r'\$\w*', '', tweet)
        tw_tokenizer = TweetTokenizer(strip_handles=True, reduce_len=True)
        temp_tw_list = tw_tokenizer.tokenize(sent_no_tickers)
        # Remove stopwords
        list_no_stopwords = [i for i in temp_tw_list if i.lower() not in self._cache_english_stopwords]
        # Remove hyperlinks
        list_no_hyperlinks = [re.sub(r'https?:\/\/.*\/\w*', '', i) for i in list_no_stopwords]
        # Remove hashtags
        list_no_hashtags = [re.sub(r'#', '', i) for i in list_no_hyperlinks]
        # Remove Punctuation and split 's, 't, 've with a space for filter
        list_no_punctuation = [re.sub(r'[' + string.punctuation + ']+', ' ', i) for i in list_no_hashtags]
        # Remove multiple whitespace
        new_sent = ' '.join(list_no_punctuation)
        # Remove any words with 2 or fewer letters
        filtered_list = tw_tokenizer.tokenize(new_sent)
        list_filtered = [re.sub(r'^\w\w?$', '', i) for i in filtered_list]
        filtered_sent = ' '.join(list_filtered)
        cleaned_tweet = re.sub(r'\s\s+', ' ', filtered_sent)
        # Remove any whitespace at the front of the sentence
        cleaned_tweet = cleaned_tweet.lstrip(' ')
        return cleaned_tweet
