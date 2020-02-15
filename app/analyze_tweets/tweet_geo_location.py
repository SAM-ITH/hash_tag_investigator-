import threading

import geocoder
from geopy.geocoders import Nominatim


class tweet_geo_location(object):
    def __init__(self):
        self._geolocator = Nominatim()
        self._known_positive_location = []
        self._known_negative_location = []
        self._known_neutral_location = []
        self._unknown_positive_location = []
        self._unknown_negative_location = []
        self._unknown_neutral_location = []

    def find_locations(self, tweet_list):
        # split work for threads
        thread_count = len(tweet_list) / 25
        if (len(tweet_list) % 25) > 0:
            thread_count += 1

        threads = []
        start_index = 0
        for thread_index in range(1, int(thread_count + 1)):
            if (start_index + 25) < len(tweet_list):
                end_index = start_index + 24
            else:
                end_index = len(tweet_list) - 1

            t = threading.Thread(name="worker-" + str(thread_index), target=self.worker,
                                 args=(tweet_list, start_index, end_index))
            t.start()
            threads.append(t)
            start_index += 25

        for thread in threads:
            # join threads
            thread.join()

    def worker(self, tweet_list, start, end):
        for tweet in tweet_list[start: end]:
            if tweet['user']['location']:
                # location found
                try:
                    # location = self._geolocator.geocode(tweet['user']['location'], timeout=10)
                    # if hasattr(location, 'latitude') & hasattr(location, 'longitude'):
                    #     if tweet['sentiment'] == "positive":
                    #         self._known_positive_location.append({
                    #             'lat': location.latitude,
                    #             'lng': location.longitude
                    #         })
                    #     elif tweet['sentiment'] == "negative":
                    #         self._known_negative_location.append({
                    #             'lat': location.latitude,
                    #             'lng': location.longitude
                    #         })
                    #     elif tweet['sentiment'] == "neutral":
                    #         self._known_neutral_location.append({
                    #             'lat': location.latitude,
                    #             'lng': location.longitude
                    #         })
                    # else:
                    #     # location not found
                    #     if tweet['sentiment'] == "positive":
                    #         self._unknown_positive_location.append(tweet)
                    #     elif tweet['sentiment'] == "negative":
                    #         self._unknown_negative_location.append(tweet)
                    #     elif tweet['sentiment'] == "neutral":
                    #         self._unknown_neutral_location.append(tweet)
                    location = geocoder.google(tweet['user']['location'])
                    if len(location.latlng) == 2:
                        if tweet['sentiment'] == "positive":
                            self._known_positive_location.append({
                                'lat': location.latlng[0],
                                'lng': location.latlng[1],
                            })
                        elif tweet['sentiment'] == "negative":
                            self._known_negative_location.append({
                                'lat': location.latlng[0],
                                'lng': location.latlng[1],
                            })
                        elif tweet['sentiment'] == "neutral":
                            self._known_neutral_location.append({
                                'lat': location.latlng[0],
                                'lng': location.latlng[1],
                            })
                    else:
                        # location not found
                        if tweet['sentiment'] == "positive":
                            self._unknown_positive_location.append(tweet)
                        elif tweet['sentiment'] == "negative":
                            self._unknown_negative_location.append(tweet)
                        elif tweet['sentiment'] == "neutral":
                            self._unknown_neutral_location.append(tweet)
                except Exception as e:
                    print("Error: geocode failed on input %s with message %s" % (tweet['user']['location'], e.msg))
                    if tweet['sentiment'] == "positive":
                        self._unknown_positive_location.append(tweet)
                    elif tweet['sentiment'] == "negative":
                        self._unknown_negative_location.append(tweet)
                    elif tweet['sentiment'] == "neutral":
                        self._unknown_neutral_location.append(tweet)
            else:
                # location not found
                if tweet['sentiment'] == "positive":
                    self._unknown_positive_location.append(tweet)
                elif tweet['sentiment'] == "negative":
                    self._unknown_negative_location.append(tweet)
                elif tweet['sentiment'] == "neutral":
                    self._unknown_neutral_location.append(tweet)

    def get_locations(self):
        temp = {
            'positive': {
                'known': self._known_positive_location,
                'unknown': self._unknown_positive_location
            },
            'negative': {
                'known': self._known_negative_location,
                'unknown': self._unknown_negative_location
            },
            'neutral': {
                'known': self._known_neutral_location,
                'unknown': self._unknown_neutral_location
            }
        }
        return temp
