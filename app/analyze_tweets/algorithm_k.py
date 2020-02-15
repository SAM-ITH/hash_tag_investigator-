import csv
import os

import emoji
from nltk import classify, NaiveBayesClassifier

# holds directory path
dir_path = os.path.dirname(os.path.realpath(__file__))
# split index
split_index_point = 100


class Classifire(object):
    vocabulary = None
    trained_NB_Classifier = None

    def __init__(self):
        self.emoji_list = {}
        self.build_classifier()
        self.bootstrap()

    def build_classifier(self):
        # load training data set
        # with open(dir_path + "\\..\\dataset\\test_data.csv", 'r') as training_data:
        path = '/workspace/hash-tag-investor/app/dataset/test_data.csv'
        with open(path, 'r') as training_data:
            reader = csv.reader(training_data, delimiter=',')
            training_data_list = list(reader)

            negative_reviews = []
            neutral_reviews = []
            positive_reviews = []
            for row in training_data_list:
                if row[0] == "0":
                    negative_reviews.append(row[5])
                elif row[0] == "2":
                    neutral_reviews.append(row[5])
                elif row[0] == "4":
                    positive_reviews.append(row[5])

            # ----------------------------------------------------------------------------------------------------------
            # 1. Define Vocabulary
            # ----------------------------------------------------------------------------------------------------------
            positive_word_list = [word for line in positive_reviews for word in line.split()]
            neutral_word_list = [word for line in neutral_reviews for word in line.split()]
            negative_word_list = [word for line in negative_reviews for word in line.split()]
            all_word_list = [item for sublist in [positive_word_list, neutral_word_list, negative_word_list] for item in
                             sublist]
            self.vocabulary = list(set(all_word_list))

            neg_tagged_training_review_list = [{'review': one_review.split(), 'label': 'negative'} for one_review in
                                               negative_reviews]
            neu_tagged_training_review_list = [{'review': one_review.split(), 'label': 'neutral'} for one_review in
                                               neutral_reviews]
            pos_tagged_training_review_list = [{'review': one_review.split(), 'label': 'positive'} for one_review in
                                               positive_reviews]
            full_tagged_training_data = [item for sublist in
                                         [neg_tagged_training_review_list, neu_tagged_training_review_list,
                                          pos_tagged_training_review_list] for item in sublist]
            training_data = [(review['review'], review['label']) for review in full_tagged_training_data]

            # apply NLTK Classifier
            training_features = classify.apply_features(self.extract_features, training_data)

            # ----------------------------------------------------------------------------------------------------------
            # 2. Train Classifier
            # ----------------------------------------------------------------------------------------------------------
            self.trained_NB_Classifier = NaiveBayesClassifier.train(training_features)

    # ------------------------------------------------------------------------------------------------------------------
    # 3. Extract Features
    # ------------------------------------------------------------------------------------------------------------------
    def extract_features(self, review):
        review_words = set(review)
        features = {}
        for word in self.vocabulary:
            features[word] = (word in review_words)
        return features

    # ------------------------------------------------------------------------------------------------------------------
    # 4. Classify Test Data
    # ------------------------------------------------------------------------------------------------------------------
    def naive_bayes_sentiment_calculator(self, review):
        problem_instance = review.split()
        problem_features = self.extract_features(problem_instance)

        # sentiment score
        prob_classify = self.trained_NB_Classifier.prob_classify(problem_features)
        pr_positive = prob_classify.prob('positive')
        pr_negative = prob_classify.prob('negative')
        pr_neutral = prob_classify.prob('neutral')

        # extracted emojis
        emoji_list = self.extract_emojis(review)
        count = 0
        # go through emoji list
        for emoji in emoji_list:
            if emoji in self.emoji_list:
                pr_positive += (int(self.emoji_list[emoji]['positive']) / int(self.emoji_list[emoji]['total']))
                pr_negative += (int(self.emoji_list[emoji]['negative']) / int(self.emoji_list[emoji]['total']))
                pr_neutral += (int(self.emoji_list[emoji]['neutral']) / int(self.emoji_list[emoji]['total']))
                count += 1

        if count > 0:
            pr_positive = pr_positive / (count + 1)
            pr_negative = pr_negative / (count + 1)
            pr_neutral = pr_neutral / (count + 1)

        conclusion = ""
        if pr_positive > pr_neutral and pr_positive > pr_negative:
            # positive
            conclusion = "positive"
        elif pr_neutral >= pr_positive and pr_neutral >= pr_negative:
            # negative
            conclusion = "neutral"
        elif pr_negative > pr_positive and pr_negative > pr_neutral:
            # neutral
            conclusion = "negative"

        # return self.trained_NB_Classifier.classify(problem_features)
        return conclusion

    def bootstrap(self):
        # load emoji CSV
        path = '/workspace/hash-tag-investor/app/dataset/emoji_sentiment_data.csv'
        with open(path, 'r', encoding="utf-8") as file:
            # reader = csv.reader(file, delimiter=',')
            reader = file.readlines()
            for line in reader[1:]:
                line = line.split(',')
                if line[0] not in self.emoji_list:
                    self.emoji_list[line[0]] = {
                        'positive': line[6],
                        'negative': line[4],
                        'neutral': line[5],
                        'total': line[2]
                    }

    def extract_emojis(self, text):
        temp = []
        for c in text:
            if c in emoji.UNICODE_EMOJI:
                temp.append(c)
        return temp
