# -*- coding: utf-8 -*-

import re as regex

emoticons_str = r"""
    (?:
        [:=;] # Eyes
        [oO\-]? # Nose (optional)
        [D\)\]\(\]/\\OpP] # Mouth
    )"""

regex_str = [
    emoticons_str,
    r'<[^>]+>',  # HTML tags
    r'(?:@[\w_]+)',  # @-mentions
    r"(?:\#+[\w_]+[\w\'_\-]*[\w_]+)",  # hash-tags
    r'http[s]?://(?:[a-z]|[0-9]|[$-_@.&amp;+]|[!*\(\),]|(?:%[0-9a-f][0-9a-f]))+',  # URLs

    r'(?:(?:\d+,?)+(?:\.?\d+)?)',  # numbers
    r"(?:[a-z][a-z'\-_]+[a-z])",  # words with - and '
    r'(?:[\w_]+)',  # other words
    r'(?:\S)'  # anything else
]
emoji_pattern = regex.compile("["
                              u"\U0001F600-\U0001F64F"  # emoticons
                              u"\U0001F300-\U0001F5FF"  # symbols & pictographs
                              u"\U0001F680-\U0001F6FF"  # transport & map symbols
                              u"\U0001F1E0-\U0001F1FF"  # flags (iOS)
                              "]+", flags=regex.UNICODE)

tokens_re = regex.compile(r'(' + '|'.join(regex_str) + ')', regex.VERBOSE | regex.IGNORECASE)
emoticon_re = regex.compile(r'^' + emoticons_str + '$', regex.VERBOSE | regex.IGNORECASE)
z = lambda x: regex.compile('\#').sub('', regex.compile('RT @').sub('@', x, count=1).strip())


def tokenize(s):
    # remove tweet specific chars
    s = z(s)
    # remove white spaces
    s = regex.compile("[^\w']|_").sub(" ", s)
    return tokens_re.findall(s)


def pre_process(s, lowercase=False):
    # remove urls and emoji
    s = emoji_pattern.sub('', regex.sub(
        r'''(?i)\b((?:https?://|www\d{0,3}[.]|[a-z0-9.\-]+[.][a-z]{2,4}/)(?:[^\s()<>]+|\(([^\s()<>]+|(\([^\s()<>]+\)))*\))+(?:\(([^\s()<>]+|(\([^\s()<>]+\)))*\)|[^\s`!()\[\]{};:'".,<>?«»“”‘’]))''',
        '', s)).replace(u'\ufeff', '')
    tokens = tokenize(s)
    if lowercase:
        tokens = [token if emoticon_re.search(token) else token.lower() for token in tokens]
    return " ".join(str(word) for word in tokens)
