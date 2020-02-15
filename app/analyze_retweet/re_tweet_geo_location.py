import threading

from geopy.exc import GeocoderTimedOut
from geopy.geocoders import Nominatim


class re_tweet_geo_location(object):
    def __init__(self):
        self._geolocator = Nominatim()
        self._known_tweet_location = []
        self._known_re_tweet_location = []
        self._known_comment_location = []
        self._unknown_tweet_location = []
        self._unknown_re_tweet_location = []
        self._unknown_comment_location = []

    def find_locations(self, users_list):
        # split work for threads
        thread_count = len(users_list) / 25
        if (len(users_list) % 25) > 0:
            thread_count += 1

        threads = []
        start_index = 0
        for thread_index in range(1, int(thread_count + 1)):
            if (start_index + 25) < len(users_list):
                end_index = start_index + 24
            else:
                end_index = len(users_list) - 1

            t = threading.Thread(name="worker-" + str(thread_index), target=self.worker,
                                 args=(users_list, start_index, end_index))
            t.start()
            threads.append(t)
            start_index += 25

        for thread in threads:
            # join threads
            thread.join()

    def worker(self, users_list, start, end):
        for user in users_list[start: end]:
            if user['user']['location']:
                # location found
                try:
                    location = self._geolocator.geocode(user['user']['location'], timeout=10)
                    if hasattr(location, 'latitude') & hasattr(location, 'longitude'):
                        if user['type'] == "tweet":
                            self._known_tweet_location.append({
                                'lat': location.latitude,
                                'lng': location.longitude
                            })
                        elif user['type'] == "re_tweet":
                            self._known_re_tweet_location.append({
                                'lat': location.latitude,
                                'lng': location.longitude
                            })
                        elif user['type'] == "comment":
                            self._known_comment_location.append({
                                'lat': location.latitude,
                                'lng': location.longitude
                            })
                    else:
                        # location not found
                        if user['type'] == "tweet":
                            self._unknown_tweet_location.append(user)
                        elif user['type'] == "re_tweet":
                            self._unknown_re_tweet_location.append(user)
                        elif user['type'] == "comment":
                            self._unknown_comment_location.append(user)
                except GeocoderTimedOut as e:
                    print("Error: geocode failed on input %s with message %s" % (user['location'], e.msg))
                    if user['type'] == "tweet":
                        self._unknown_tweet_location.append(user)
                    elif user['type'] == "re_tweet":
                        self._unknown_re_tweet_location.append(user)
                    elif user['type'] == "comment":
                        self._unknown_comment_location.append(user)
            else:
                # location not found
                if user['type'] == "tweet":
                    self._unknown_tweet_location.append(user)
                elif user['type'] == "re_tweet":
                    self._unknown_re_tweet_location.append(user)
                elif user['type'] == "comment":
                    self._unknown_comment_location.append(user)

    def get_locations(self):
        temp = {
            'tweet': {
                'known': self._known_tweet_location,
                'unknown': self._unknown_tweet_location
            },
            're_tweet': {
                'known': self._known_re_tweet_location,
                'unknown': self._unknown_re_tweet_location
            },
            'comment': {
                'known': self._known_comment_location,
                'unknown': self._unknown_comment_location
            }
        }
        return temp
