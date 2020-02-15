import numpy
from sklearn.linear_model import LinearRegression


class predictions_h(object):
    def __init__(self):
        # make LinearRegression model for prediction
        self._model = LinearRegression()

    # make model with values
    def make_model(self, time_series, values):
        time_series = numpy.asarray(time_series).reshape(-1, 1)
        values = numpy.asarray(values).reshape(-1, 1)
        self._model.fit(time_series, values)

    # make predictions for given values
    def make_predictions(self, predict_values):
        predict_values = numpy.asarray(predict_values).reshape(-1, 1)
        return self._model.predict(predict_values)
