/**
 * Created by buwan on 7/8/2017.
 */
app.controller('TopicAnalysisController', function TopicAnalysisController($scope, $sessionStorage, $http, $location, Map) {

    $scope.request = {
        location_1: "",
        location_2: "",
        count: {
            id: 500,
            title: "500 tweets"
        }
    };
    $scope.show_map_1 = false;
    $scope.show_map_2 = false;
    $scope.show_map_loading = false;
    var map;

    var myConfig = {
        type: 'line',
        legend: {
            adjustLayout: true,
            align: 'center',
            verticalAlign: 'bottom'
        },
        title: {
            adjustLayout: true,
            text: ""
        },
        plot: {
            marker: {
                visible: false
            }
        },
        plotarea: {
            margin: "dynamic 50 dynamic dynamic"
        },
        scaleX: {
            transform: {
                type: 'date',
                all: '%mm/%d/%y<br>%h:%i:%s'
            }
        },
        scaleY: {
            guide: {
                lineStyle: 'solid'
            },
            label: {
                text: 'Development'
            },
            markers: [
                {
                    type: 'line',
                    range: [23],
                    lineColor: '#c62828',
                    lineStyle: 'dashed',
                    label: {
                        text: '',
                        placement: 'right'
                    }
                }
            ]
        },
        tooltip: {
            text: "%v<br>%kv",
            borderRadius: 2
        },
        crosshairX: {
            exact: true,
            lineColor: '#000',
            scaleLabel: {
                borderRadius: 2
            },
            marker: {
                size: 5,
                backgroundColor: 'white',
                borderWidth: 2,
                borderColor: '#000'
            }
        },
        series: [
            {
                values: [],
                lineColor: '#1d47f2',
                text: "Likes",
                marker: {
                    backgroundColor: '#1d47f2'
                }
            },
            {
                values: [],
                lineColor: '#f57c00',
                text: "Re-Tweets",
                marker: {
                    backgroundColor: '#f57c00'
                }
            },
            {
                values: [],
                lineColor: '#35ca00',
                text: "Followers",
                marker: {
                    backgroundColor: '#35ca00'
                }
            },
            {
                values: [],
                lineColor: '#9d27ca',
                text: "Comments",
                marker: {
                    backgroundColor: '#9d27ca'
                }
            },
            {
                values: [],
                lineColor: '#000000',
                text: "Tweets",
                marker: {
                    backgroundColor: '#000000'
                }
            }
        ]
    };

    $scope.show_results = false;
    $scope.show_loading = false;

    $scope.backToHome = function () {
        $location.url('/dashboard');
    };

    $scope.res = {};

    /**
     * request data
     */
    $scope.analyze = function () {
        map = null; // clear map
        $scope.show_map_1 = false; // hide map
        $scope.show_map_2 = false; // hide map
        $scope.show_results = false; // hide results
        $scope.show_loading = true; // show loading bar
        $http({
            method: 'POST',
            url: SERVER_URL + '/analyzeRetweet',
            headers: {
                'Content-Type': 'application/json'
            },
            data: {
                topic_1: $scope.request.topic_1,
                topic_2: $scope.request.topic_2,
                count: $scope.request.count.id
            }
        }).then(function successCallback(response) {
            // load data
            loadRes('topic_1', 'chart_1', response.data.topic_1);
            loadRes('topic_2', 'chart_2', response.data.topic_2);

            // plot prediction
            plot_predictions('topic_1', 'chart_1_1', response.data.topic_1);
            plot_predictions('topic_2', 'chart_2_1', response.data.topic_2);
            $scope.show_loading = false; // hide loading bar
            $scope.show_results = true; // show results

            // load Map
            $scope.show_map_loading = true;
            loadMap("map_1", response.data.topic_1.users);
        }, function errorCallback(response) {
            console.error(response);
        });
    };

    loadRes = function (type, chart_id, data) {
        $scope.res[type] = {
            followers_count: data.followers_count,
            likes_count: data.likes_count,
            re_tweets: data.re_tweet_count,
            comments_count: data.comments_count,
            start: new Date(Object.keys(data.likes_timeline)[0] * 1000),
            end: new Date(Object.keys(data.likes_timeline)[Object.keys(data.likes_timeline).length - 1] * 1000)
        };

        // reset values
        myConfig.title.text = $scope.request[type] + " - Analysis";
        myConfig.series[0].values = [];
        myConfig.series[1].values = [];
        myConfig.series[2].values = [];
        myConfig.series[3].values = [];
        myConfig.series[4].values = [];
        angular.forEach(data.followers_timeline, function (value, key) {
            myConfig.series[0].values.push([(key * 1000), data.likes_timeline[key]]);
            myConfig.series[1].values.push([(key * 1000), data.re_tweet_timeline[key]]);
            myConfig.series[2].values.push([(key * 1000), data.followers_timeline[key]]);
            myConfig.series[3].values.push([(key * 1000), data.comments_timeline[key]]);
            myConfig.series[4].values.push([(key * 1000), data.tweet_timeline[key]]);
        });
        zingchart.render({
            id: chart_id,
            data: myConfig,
            height: '100%',
            width: '100%'
        });
    };

    plot_predictions = function (type, chart_id, data) {
        myConfig.title.text = $scope.request[type] + " - Predictions";
        myConfig.plot = {
            marker: {
                visible: false
            }
        };
        myConfig.series[0].values = [];
        myConfig.series[1].values = [];
        myConfig.series[2].values = [];
        myConfig.series[3].values = [];
        myConfig.series[4].values = [];
        for (var i = 0; i < data.predicting_timeline.length; i++) {
            myConfig.series[0].values.push([(data.predicting_timeline[i] * 1000), parseInt(data.likes_predictions[i])]);
            myConfig.series[1].values.push([(data.predicting_timeline[i] * 1000), parseInt(data.re_tweets_predictions[i])]);
            myConfig.series[2].values.push([(data.predicting_timeline[i] * 1000), parseInt(data.followers_predictions[i])]);
            myConfig.series[3].values.push([(data.predicting_timeline[i] * 1000), parseInt(data.comments_predictions[i])]);
            myConfig.series[4].values.push([(data.predicting_timeline[i] * 1000), parseInt(data.tweets_predictions[i])]);
        }
        zingchart.render({
            id: chart_id,
            data: myConfig,
            height: '100%',
            width: '100%'
        });
    };

    loadMap = function (map_type, data) {
        $http({
            method: 'POST',
            url: SERVER_URL + '/retweetGeoCoordinates',
            headers: {
                'Content-Type': 'application/json'
            },
            data: data
        }).then(function successCallback(response) {
            // console.log(response);
            $scope.show_map_loading = false;
            map = Map.init("map_1"); // initialize map
            $scope.show_map_1 = true;

            // load tweet known markers
            for (var i = 0; i < response.data.tweet.known.length; i++) {
                Map.addMarker("tweet", response.data.tweet.known[i], map);
            }
            // load re tweet known markers
            for (var x = 0; x < response.data.re_tweet.known.length; x++) {
                Map.addMarker("re_tweet", response.data.re_tweet.known[x], map);
            }
            // load comment known markers
            for (var z = 0; z < response.data.comment.known.length; z++) {
                Map.addMarker("comment", response.data.comment.known[z], map);
            }
        }, function errorCallback(response) {
            console.error(response);
        });
    }
});