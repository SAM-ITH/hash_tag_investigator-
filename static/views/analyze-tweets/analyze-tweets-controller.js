/**
 * Created by buwan on 7/8/2017.
 */
app.controller('AnalyzeTweetsController', function AnalyzeTweetsController($scope, $sessionStorage, $http, NgMap, $location, Map) {
    var results = [];

    $scope.result = {};
    $scope.last_index = -1; // holds last clicked index
    $scope.show_results = false;
    $scope.show_loading = false;
    $scope.show_fake_results = false;
    $scope.show_fake_loading = false;
    $scope.filter_false_tweets = [];
    $scope.show_map_loading = false;
    $scope.show_map_1 = false;
    var map;

    // pie chart config
    var myConfig = {
        backgroundColor: '#FBFCFE',
        type: "ring",
        title: {
            text: "Sentiment Results",
            fontSize: 20,
            // border: "1px solid black",
            padding: "15",
            fontColor: "#000000",
        },
        plot: {
            slice: '50%',
            borderWidth: 0,
            backgroundColor: '#FBFCFE',
            animation: {
                effect: 2,
                sequence: 3
            },
            valueBox: [
                {
                    type: 'all',
                    text: '%t',
                    placement: 'out'
                },
                {
                    type: 'all',
                    text: '%npv%',
                    placement: 'in'
                }
            ]
        },
        tooltip: {
            fontSize: 16,
            anchor: 'c',
            x: '50%',
            y: '50%',
            sticky: true,
            backgroundColor: 'none',
            borderWidth: 0,
            thousandsSeparator: ',',
            text: '',
            mediaRules: [
                {
                    maxWidth: 500,
                    y: '54%',
                }
            ]
        },
        plotarea: {
            backgroundColor: 'transparent',
            borderWidth: 0,
            borderRadius: "0 0 0 10",
            margin: "70 0 10 0"
        },
        legend: {
            toggleAction: 'remove',
            backgroundColor: '#FBFCFE',
            borderWidth: 0,
            adjustLayout: true,
            align: 'center',
            verticalAlign: 'bottom',
            marker: {
                type: 'circle',
                cursor: 'pointer',
                borderWidth: 0,
                size: 5
            },
            item: {
                fontColor: "#777",
                cursor: 'pointer',
                offsetX: -6,
                fontSize: 12
            },
            mediaRules: [
                {
                    maxWidth: 500,
                    visible: false
                }
            ]
        },
        scaleR: {
            refAngle: 270
        },
        series: []
    };

    $scope.quantities = [{
        id: 1000,
        title: "1000 tweets"
    }];

    $scope.request = {
        text: "",
        count: $scope.quantities[0]
    };

    $scope.backToHome = function () {
        $location.url('/dashboard');
    };
    $scope.__init__ = function () {

    };

    /**
     * filter data
     *
     * @param type
     */
    $scope.filter_data = function (type) {
        $scope.result.tweets = [];
        if ($scope.last_index == type) {
            $scope.result.tweets = results.tweets;
            $scope.last_index = -1;
        } else {
            for (var i = 0; i < results.tweets.length; i++) {
                if (
                    (results.tweets[i].sentiment == 'positive' && type == 0)
                    ||
                    (results.tweets[i].sentiment == 'neutral' && type == 1)
                    ||
                    (results.tweets[i].sentiment == 'negative' && type == 2)
                ) {
                    $scope.result.tweets.push(results.tweets[i]);
                }
            }
            $scope.last_index = type;
        }
        $scope.$apply();
    };

    /**
     * request data
     */
    $scope.analyze = function () {
        if (validate()) {
            myConfig.series = []; // reset data
            $scope.show_results = false; // hide results
            $scope.show_loading = true; // show loading bar
            $scope.show_fake_results = false;
            $scope.show_fake_loading = false;
            $scope.show_map_loading = false;
            $scope.show_map_1 = false;
            $http({
                method: 'POST',
                url: SERVER_URL + '/analyzeTweet',
                headers: {
                    'Content-Type': 'application/json'
                },
                data: {
                    text: $scope.request.text,
                    count: $scope.request.count.id
                }
            }).then(function successCallback(response) {
                // parse data to local obj
                $scope.result = angular.copy(response.data);
                results = angular.copy(response.data); // keep copy
                // load chart
                loadChart(response);
                $scope.show_loading = false; // hide loading bar
                $scope.show_results = true; // show results

                // load Map
                $scope.show_map_loading = true;
                loadMap("map_1", response.data.tweets);
            }, function errorCallback(response) {
                console.error(response);
            });
        }
    };

    function loadChart(response) {
        // process data
        var total = response.data.positive_count + response.data.neutral_count + response.data.negative_count;
        var pos = ((response.data.positive_count / total) * 100);
        var nue = ((response.data.neutral_count / total) * 100);
        var neg = ((response.data.negative_count / total) * 100);
        myConfig.series.push({
            text: "positive",
            values: [pos],
            lineColor: "#1d47f2",
            backgroundColor: "#1d47f2",
            lineWidth: 1,
            marker: {
                backgroundColor: '#1d47f2'
            }
        });
        myConfig.series.push({
            text: "neutral",
            values: [nue],
            lineColor: "#e8a900",
            backgroundColor: "#e8a900",
            lineWidth: 1,
            marker: {
                backgroundColor: '#e8a900'
            }
        });
        myConfig.series.push({
            text: "negative",
            values: [neg],
            lineColor: "#af0d00",
            backgroundColor: "#af0d00",
            lineWidth: 1,
            marker: {
                backgroundColor: '#af0d00'
            }
        });
        zingchart.render({
            id: 'myChart',
            data: {
                graphset: [myConfig]
            },
            height: '498',
            width: '100%'
        });
    }

    zingchart.node_click = function (p) {
        $scope.filter_data(p.plotindex);
    };

    /**
     * Reset data to original
     */
    $scope.resetFilter = function () {
        zingchart.exec('myChart', 'reload');
        $scope.result = angular.copy(results);
    };

    /**
     * Filter False Tweets
     */
    $scope.filterFalseTweets = function () {
        $scope.show_fake_results = false;
        $scope.show_fake_loading = true;
        $scope.filter_false_tweets = [];
        $http({
            method: 'POST',
            url: SERVER_URL + '/analyzeFalseTweets',
            headers: {
                'Content-Type': 'application/json'
            },
            data: {
                tweets: $scope.result['tweets']
            }
        }).then(function successCallback(response) {
            $scope.filter_false_tweets = response.data;
            $scope.show_fake_results = true;
            $scope.show_fake_loading = false;
        }, function errorCallback(response) {
            console.error(response);
        });
    };

    function validate() {
        var status = false;
        if ($scope.request.text.trim() === "") {
            $.amaran({
                'message': 'Enter text you want to search',
                'position': 'bottom right'
            });
        } else {
            status = true;
        }

        return status;
    }

    loadMap = function (map_type, data) {

        $http({
            method: 'POST',
            url: SERVER_URL + '/tweetGeoCoordinates',
            headers: {
                'Content-Type': 'application/json'
            },
            data: data
        }).then(function successCallback(response) {
            $scope.show_map_loading = false;
            map = Map.init("map_1"); // initialize map
            $scope.show_map_1 = true;

            // load positive tweet known markers
            for (var i = 0; i < response.data.positive.known.length; i++) {
                Map.addMarker("positive", response.data.positive.known[i], map);
            }
            // load negative tweet known markers
            for (var x = 0; x < response.data.negative.known.length; x++) {
                Map.addMarker("negative", response.data.negative.known[x], map);
            }
            // load neutral tweet known markers
            for (var z = 0; z < response.data.neutral.known.length; z++) {
                Map.addMarker("neutral", response.data.neutral.known[z], map);
            }
        }, function errorCallback(response) {
            console.error(response);
        });
    }
});