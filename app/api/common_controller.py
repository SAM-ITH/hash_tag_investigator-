# def download_tweets(query):
#     # connect with tweeter API
#     api = TwitterAPI(config.consumer_key, config.consumer_secret, config.access_token, config.access_token_secret)
#
#     # query the tweeter with given 'query' param through the API
#     results = api.request('search/tweets', {'q': query, 'count': 150})
#
#     # loop through the queried results
#     for item in results:
#         # save results into DB
#         DB.dbConnection.tweets[query].save({
#             'id': item['id'],
#             'text': item['text'],
#             'hashtags': item['entities']['hashtags'],
#             'symbols': item['entities']['symbols']
#         })
#         # print(item)
#
#     # print out the Quota details of the using tweeter account
#     print('\nQUOTA: %s' % results.get_rest_quota())
