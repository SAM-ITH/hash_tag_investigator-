/**
 * Created by buwan on 7/8/2017.
 */
app.controller('EventAnalysisController', function EventAnalysisController($scope, $sessionStorage, $http, $location) {
    $scope.show_results = false;
    $scope.show_loading = false;
    $scope.show_account_loading = false;
    $scope.show_account_results = false;
    $scope.show_analyzed_profile = false;
    $scope.show_analyzed_profile_loading = false;
    $scope.show_analyzed_hash_tags = false;

    $scope.account_request = {
        user: ''
    };

    $scope.searched_users = [];
    $scope.selected_user = {};
    $scope.recent_tweets = [];
    $scope.recent_hash_tags = [];

    $scope.quantities = [{
        id: 10,
        title: "10 tweets"
    }, {
        id: 20,
        title: "20 tweets"
    }, {
        id: 50,
        title: "50 tweets"
    }, {
        id: 80,
        title: "80 tweets"
    }, {
        id: 100,
        title: "100 tweets"
    }, {
        id: 150,
        title: "150 tweets"
    }, {
        id: 200,
        title: "200 tweets"
    }, {
        id: 500,
        title: "500 tweets"
    }, {
        id: 1000,
        title: "1000 tweets"
    }];

    $scope.request = {
        topic: "",
        count: $scope.quantities[8]
    };


    var time_series_config = {
        type: 'line',
        legend: {
            adjustLayout: true,
            align: 'center',
            verticalAlign: 'bottom'
        },
        title: {
            adjustLayout: true,
            text: "Tweets Time Line"
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
                text: 'No of Tweets'
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
                lineColor: '#f57c00',
                marker: {
                    backgroundColor: '#f57c00'
                }
            }
        ]
    };

    var bar_chart_config = {
        "type": "bar3d",
        "background-color": "#fff",
        "3d-aspect": {
            "true3d": 0,
            "y-angle": 10,
            "depth": 30
        },
        "title": {
            "text": "Most Discussed Topics",
            "height": "40px",
            "font-weight": "normal",
            "text-color": "#ffffff"
        },
        "legend": {
            "layout": "float",
            "background-color": "none",
            "border-color": "none",
            "item": {
                "font-color": "#333"
            },
            "x": "37%",
            "y": "10%",
            "width": "90%",
            "shadow": 0
        },
        "plotarea": {
            "margin": "95px 35px 50px 70px",
            "background-color": "#fff",
            "alpha": 0.3
        },
        "scale-y": {
            "background-color": "#fff",
            "border-width": "1px",
            "border-color": "#333",
            "alpha": 0.5,
            "format": "%v",
            "guide": {
                "line-style": "solid",
                "line-color": "#333",
                "alpha": 0.2
            },
            "tick": {
                "line-color": "#333",
                "alpha": 0.2
            },
            "item": {
                "font-color": "#333",
                "padding-right": "6px"
            }
        },
        "scale-x": {
            "background-color": "#fff",
            "border-width": "1px",
            "border-color": "#333",
            "alpha": 0.5,
            "values": [],
            "guide": {
                "visible": false
            },
            "tick": {
                "line-color": "#333",
                "alpha": 0.2
            },
            "item": {
                "font-size": "11px",
                "font-color": "#333"
            }
        },
        "series": [
            {
                "values": [],
                "text": "",
                "background-color": "#03A9F4 #4FC3F7",
                "border-color": "#673AB7",
                "legend-marker": {
                    "border-color": "#673AB7"
                },
                "tooltip": {
                    "background-color": "#673AB7",
                    "text": "%v",
                    "font-size": "12px",
                    "padding": "6 12",
                    "border-color": "none",
                    "shadow": 0,
                    "border-radius": 5
                }
            }
        ]
    };

    $scope.backToHome = function () {
        $location.url('/dashboard');
    };

    /**
     * request data
     */
    $scope.analyze = function () {
        if (validate_1()) {
            $scope.show_results = false; // hide results
            $scope.show_loading = true; // show loading bar
            $http({
                method: 'POST',
                url: SERVER_URL + '/analyzeEvent',
                headers: {
                    'Content-Type': 'application/json'
                },
                data: {
                    topic: $scope.request.topic,
                    count: $scope.request.count.id
                }
            }).then(function successCallback(response) {
                loadChart(response.data['time_series']);
                loadForecast(response.data['forecast']);
                loadBarChart(response.data['clustered_words']);
                $scope.show_loading = false; // hide loading bar
                $scope.show_results = true; // show results
            }, function errorCallback(response) {
                console.error(response);
            });
        }
    };

    function validate_1() {
        var status = false;
        if ($scope.request.topic === "") {
            $.amaran({
                'message': 'Enter event you want to search',
                'position': 'bottom right'
            });
        } else {
            status = true;
        }

        return status;
    }

    loadChart = function (data) {
        time_series_config.title.text = "Tweets Time Line";
        time_series_config.series = [{
            values: [],
            lineColor: '#f57c00',
            marker: {
                backgroundColor: '#f57c00'
            }
        }];
        angular.forEach(data, function (value, key) {
            time_series_config.series[0].values.push([(key * 1000), value.length]);
        });
        zingchart.render({
            id: 'chart_1',
            data: time_series_config,
            height: '100%',
            width: '100%'
        });
    };

    loadForecast = function (data) {
        time_series_config.title.text = "Tweets Forecast";
        time_series_config.series = [{
            values: [],
            lineColor: '#1667f2',
            marker: {
                backgroundColor: '#1667f2'
            }
        }];
        angular.forEach(data, function (value, key) {
            time_series_config.series[0].values.push([(parseInt(key) * 1000), parseInt(value)]);
        });
        zingchart.render({
            id: 'chart_2',
            data: time_series_config,
            height: '100%',
            width: '100%'
        });
    };

    loadBarChart = function (data) {
        // reset data
        bar_chart_config['scale-x'].values = [];
        bar_chart_config['series'][0].values = [];
        for (var i = Object.keys(data).length - 1; i > Object.keys(data).length - 6; i--) {
            for (var x = 0; x < data[Object.keys(data)[i]].length; x++) {
                bar_chart_config['scale-x'].values.push(data[Object.keys(data)[i]][x]);
                bar_chart_config['series'][0].values.push(parseInt(Object.keys(data)[i]));
            }
        }
        zingchart.render({
            id: 'chart_3',
            data: bar_chart_config,
            height: '100%',
            width: '100%',
            defaults: {
                'font-family': 'sans-serif'
            }
        });
    };

    $scope.analyzeAccount = function () {
        if (validate_2()) {
            $scope.show_account_loading = true;
            $scope.show_account_results = false;
            $http({
                method: 'POST',
                url: SERVER_URL + '/getUsers',
                headers: {
                    'Content-Type': 'application/json'
                },
                data: $scope.account_request
            }).then(function successCallback(response) {
                $scope.searched_users = [];
                for (var i = 0; i < response.data.length; i++) {
                    $scope.searched_users.push(response.data[i]);
                }
                $scope.show_account_loading = false;
                $scope.show_account_results = true;
            }, function errorCallback(response) {
                console.error(response);
            });
        }
    };

    function validate_2() {
        var status = false;
        if ($scope.account_request.user === "") {
            $.amaran({
                'message': 'Enter user`s name to search',
                'position': 'bottom right'
            });
        } else {
            status = true;
        }

        return status;
    }

    $scope.user_on_click = function (user) {
        $scope.selected_user = user;
        $scope.show_analyzed_profile = false;
        $scope.show_analyzed_profile_loading = false;
        $scope.show_analyzed_hash_tags = false;
        $('#user_model').modal('show');
    };

    $scope.parseDate = function (date) {
        return new Date(date);
    };

    $scope.userProfileAnalysis = function () {
        $scope.show_analyzed_profile_loading = true;
        $scope.show_analyzed_profile = false;
        $scope.show_analyzed_hash_tags = false;
        $http({
            method: 'POST',
            url: SERVER_URL + '/analyseUserProfile',
            headers: {
                'Content-Type': 'application/json'
            },
            data: {
                id: $scope.selected_user.id
            }
        }).then(function successCallback(response) {
            $scope.recent_tweets = response.data['recent_tweets'];
            $scope.show_analyzed_profile_loading = false;
            $scope.show_analyzed_profile = true;

            // show hash tags
            $scope.recent_hash_tags = [];
            if (Object.keys(response.data['hash_tags']).length > 0) {
                for (var i = 0; i < Object.keys(response.data['hash_tags']).length; i++) {
                    $scope.recent_hash_tags.push(Object.keys(response.data['hash_tags'])[i]);
                }
                $scope.show_analyzed_hash_tags = true;
            }
        }, function errorCallback(response) {
            console.error(response);
        });
    }
});