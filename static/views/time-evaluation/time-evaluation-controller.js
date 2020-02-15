/**
 * Created by buwan on 7/8/2017.
 */
app.controller('TimeEvaluationController', function TimeEvaluationController($scope, $sessionStorage, $http, $location) {
    var results = {};
    $scope.tweets_set_1 = [];
    $scope.tweets_set_2 = [];
    $scope.show_results = false;
    $scope.show_loading = false;
    $scope.request = {
        topic_1: "",
        topic_2: "",
        count: {
            id: 200,
            title: "200 tweets"
        }
    };
    $scope.categories = [
        {status: true, title: "Price"},
        {status: false, title: "Camera"},
        {status: false, title: "Battery Life"},
        {status: false, title: "RAM"},
        {status: false, title: "Performance"}
    ];
    $scope.most_popular = "";
    // for all 5 categories
    var colors = ["#00ab08", "#0117ab", "#af001d", "#f5c200", "#9d27ca"];
    var colors_2 = ["#74ab89", "#4b5aab", "#e85d6f", "#f5e197", "#b285ca"];

    // time series line chart
    var config_time_series = {
        backgroundColor: '#FBFCFE',
        type: "bar",
        title: {
            // text: "Economic growth in Greece vs Euro Zone",
            text: "Timely Evaluation of Categories",
            align: "left",
            fontFamily: 'Lato',
            fontSize: 16,
            padding: "15",
            fontColor: "#1E5D9E",
        },
        subtitle: {
            text: "",
            align: "left",
            fontFamily: 'Lato',
            fontSize: 12,
            fontColor: "#777",
            padding: "15"
        },
        source: {
            text: "",
            fontColor: "#777",
            fontFamily: 'Lato'
        },
        legend: {
            layout: "x2",
            align: 'right',
            borderWidth: "0px",
            marker: {
                borderRadius: 50
            },
            item: {
                fontColor: "#777"
            }
        },
        plot: {
            backgroundColor: '#FBFCFE',
            marker: {
                size: 3.5
            },
            tooltip: {
                visible: false
            },
            barSpace: "2"
        },
        plotarea: {
            margin: "90 50 50 50"
        },
        scaleX: {
            offsetY: -20,
            lineWidth: 0,
            padding: 20,
            margin: 20,
            item: {
                padding: 5,
                fontColor: "#0a0a0a",
                fontFamily: 'Montserrat'
            },
            tick: {
                lineColor: '#D1D3D4'
            },
            guide: {
                visible: true,
                lineColor: '#D7D8D9',
                lineStyle: 'dotted',
                lineGapSize: '4px',
                rules: [
                    {
                        rule: "%i == 0",
                        visible: false
                    }
                ]
            },
            transform: {
                type: 'date',
                all: '%m/%d/%y'
            },
            values: []
        },
        scaleY: {
            maxValue: 8,
            lineWidth: 0,
            item: {
                padding: "0 10 0 0",
                fontColor: "#1E5D9E",
                fontFamily: 'Montserrat'
            },
            tick: {
                lineColor: '#D1D3D4'
            },
            guide: {
                visible: true,
                lineColor: '#D7D8D9',
                lineStyle: 'dotted',
                lineGapSize: '4px',
                rules: [
                    {
                        rule: "%i == 0",
                        visible: false
                    }
                ]
            }
        },
        crosshairX: {
            lineColor: "#b6b6b6",
            trigger: "move",
            lineStyle: 'dashed',
            marker: {
                visible: true,
                size: 4
            },
            scaleLabel: {
                bold: true,
                backgroundColor: "#FBFCFE",
                fontColor: "#1E5D9E",
                fontSize: "16px",
                callout: false,
                paddingTop: 2,

            },
            plotLabel: {
                backgroundColor: "white",
                borderColor: "#e3e3e3",
                borderRadius: "5px",
                bold: true,
                fontSize: "12px",
                fontFamily: "Lato",
                fontColor: "#2f2f2f",
                textAlign: 'right',
                padding: '15px',
                shadow: true,
                shadowAlpha: 0.2,
                shadowBlur: 5,
                shadowDistance: 4,
                shadowColor: "#a1a1a1",

            }
        },
        series: []
    };

    var hbar_chart = {
        type: "hbar",
        backgroundColor: "#2b2b2b",
        tooltip: {visible: false},
        scaleX: {
            lineColor: "transparent",
            tick: {
                visible: false
            },
            labels: [],
            item: {
                fontColor: "#e8e8e8",
                fontSize: 14
            }
        },
        scaleY: {
            visible: false,
            lineColor: "transparent",
            guide: {
                visible: false
            },
            tick: {
                visible: false
            }
        },
        plotarea: {
            marginLeft: "90",
            marginTop: "30",
            marginBottom: "30"
        },
        plot: {
            stacked: true,
            barsSpaceLeft: "20px",
            barsSpaceRight: "20px",
            valueBox: {
                visible: true,
                text: "%v%",
                fontColor: "#2A2B3A",
                fontSize: 14
            },
            tooltip: {
                borderWidth: 0,
                borderRadius: 2
            },
            animation: {
                effect: 3,
                sequence: 3,
                method: 3
            }
        },
        series: [
            {
                values: [],
                borderRadius: "50px 0px 0px 50px",
                backgroundColor: "#E71D36",
                rules: []
            },
            {
                values: [],
                borderRadius: "0px 50px 50px 0px",
                backgroundColor: "#E71D36",
                //alpha : 0.8,
                rules: []
            }
        ]
    };

    var pie_chart_config = {
        type: "pie",
        backgroundColor: "#2b2b2b",
        plot: {
            borderColor: "#2B313B",
            borderWidth: 5,
            valueBox: {
                placement: 'out',
                text: '%t\n%npv%',
                fontFamily: "Lato"
            },
            tooltip: {
                fontSize: '18',
                fontFamily: "Open Sans",
                padding: "5 10",
                text: "%npv%"
            },
            animation: {
                effect: 2,
                method: 5,
                speed: 500,
                sequence: 1
            }
        },
        title: {
            fontColor: "#fff",
            text: '',
            align: "left",
            offsetX: 10,
            fontFamily: "Lato",
            fontSize: 25
        },
        subtitle: {
            offsetX: 10,
            offsetY: 10,
            fontColor: "#8e99a9",
            fontFamily: "Lato",
            fontSize: "16",
            text: '',
            align: "left"
        },
        plotarea: {
            margin: "20 0 0 0"
        },
        series: [
            {
                values: [],
                text: "",
                backgroundColor: '#ffffff',
            },
            {
                values: [],
                text: "",
                backgroundColor: '#f5c200'
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
        if (validate()) {
            $scope.show_results = false; // hide results
            $scope.show_loading = true; // show loading bar
            $http({
                method: 'POST',
                url: SERVER_URL + '/compareTopics',
                headers: {
                    'Content-Type': 'application/json'
                },
                data: {
                    topic_1: $scope.request.topic_1,
                    topic_2: $scope.request.topic_2,
                    count: $scope.request.count.id,
                    categories: $scope.categories
                }
            }).then(function successCallback(response) {
                console.log(response);
                // copy results
                results = angular.copy(response.data);
                // set tweets set
                $scope.tweets_set_1 = angular.copy(response.data.topic_1_tweets);
                $scope.tweets_set_2 = angular.copy(response.data.topic_2_tweets);
                // display chart
                displayChart(results);
                $scope.show_loading = false; // hide loading bar
                $scope.show_results = true; // show results
            }, function errorCallback(response) {
                console.error(response);
            });
        }
    };

    function validate() {
        var status = false;
        if ($scope.request.topic_1.trim() == "" || $scope.request.topic_2.trim() == "") {
            $.amaran({
                'message': 'Enter Analyzing Topics',
                'position': 'bottom right'
            });
        } else {
            status = true;
        }

        var category = false;
        for (var i = 0; i < $scope.categories.length; i++) {
            if ($scope.categories[i].status) {
                category = true;
                break;
            }
        }
        if (!category) {
            $.amaran({
                'message': 'Select at least one category',
                'position': 'bottom right'
            });
        }
        if (status && category)
            return true;
        return false;
    }

    function displayChart(results) {
        for (var i = 1; i <= 2; i++) {
            make_time_series(results, i, 'chart_' + i);
        }
        make_pie_chart(results);
    }

    function make_time_series(data, topic_id, chart_id) {
        var hbar_values = [];
        // reset values
        config_time_series.scaleX.values = [];
        config_time_series.series = [];
        var first = true;
        var cat_counter = 0;
        var values = [];
        var total_hits = 0;
        angular.forEach(data['topic_' + topic_id + '_tweet_count'], function (value, key) {
            // set hbar values
            var temp_hbar_value = {
                name: key,
                total: 0
            };
            values = [];
            angular.forEach(value, function (inner_value, inner_key) {
                if (first) {
                    config_time_series.scaleX.values.push((inner_key * 1000));
                }
                values.push(inner_value);
                temp_hbar_value.total += inner_value;
            });
            config_time_series.series.push({
                text: key,
                values: values,
                backgroundColor: colors[cat_counter]
            });
            cat_counter++;
            first = false;
            hbar_values.push(temp_hbar_value);
            total_hits += temp_hbar_value.total;
        });
        zingchart.render({
            id: chart_id,
            data: {
                graphset: [config_time_series]
            },
            height: '100%',
            width: '100%'
        });
        // make hbar chart
        make_hbar_chart(hbar_values, total_hits, topic_id);
    }

    function make_hbar_chart(data, total, chart_id) {
        // clear values
        hbar_chart.scaleX.labels = [];
        hbar_chart.series[0].values = [];
        hbar_chart.series[1].values = [];
        hbar_chart.series[0].rules = [];
        hbar_chart.series[1].rules = [];

        for (var i = (data.length - 1); i >= 0; i--) {
            // set name
            hbar_chart.scaleX.labels.push(data[i].name);
            hbar_chart.series[0].values.push(parseInt((data[i].total / total) * 100));
            hbar_chart.series[0].rules.push({
                rule: "%i === " + i,
                backgroundColor: colors[i]
            });

            hbar_chart.series[1].values.push(parseInt((100 - (data[i].total / total) * 100)));
            hbar_chart.series[1].rules.push({
                rule: "%i === " + i,
                backgroundColor: colors_2[i]
            });
        }
        zingchart.render({
            id: 'hbar_' + chart_id,
            data: hbar_chart,
            height: '100%',
            width: '100%'
        });
    }

    function make_pie_chart(data) {
        var main_positive = 0;
        var pr_values = [];
        for (var i = 1; i <= 2; i++) {
            main_positive += ((data['topic_' + i + '_positive'] / data['topic_' + i + '_total'])) * 100;
            pr_values.push(((data['topic_' + i + '_positive'] / data['topic_' + i + '_total'])) * 100);
        }
        main_positive = main_positive / 2;
        pie_chart_config.series[0].values = [parseInt(main_positive)];
        pie_chart_config.series[1].values = [100 - parseInt(main_positive)];

        if (pie_chart_config.series[0].values[0] >= pie_chart_config.series[1].values[0]) {
            if (pr_values[0] >= pr_values[1]) {
                pie_chart_config.series[0].text = $scope.request.topic_1;
                pie_chart_config.series[1].text = $scope.request.topic_2;
                $scope.most_popular = $scope.request.topic_1;
            } else {
                pie_chart_config.series[0].text = $scope.request.topic_2;
                pie_chart_config.series[1].text = $scope.request.topic_1;
                $scope.most_popular = $scope.request.topic_2;
            }
        } else {
            if (pr_values[0] >= pr_values[1]) {
                pie_chart_config.series[1].text = $scope.request.topic_1;
                pie_chart_config.series[0].text = $scope.request.topic_2;
                $scope.most_popular = $scope.request.topic_1;
            } else {
                pie_chart_config.series[1].text = $scope.request.topic_2;
                pie_chart_config.series[0].text = $scope.request.topic_1;
                $scope.most_popular = $scope.request.topic_2;
            }
        }
        zingchart.render({
            id: 'pie_chart',
            data: pie_chart_config,
            height: '100%',
            width: '100%'
        });
    }
});