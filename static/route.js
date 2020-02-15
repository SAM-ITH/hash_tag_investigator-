/**
 * Created by buwan on 7/6/2017.
 */
app.config(['$locationProvider', '$routeProvider',
    function ($locationProvider, $routeProvider) {
        $locationProvider.hashPrefix('!');

        $routeProvider.when('/login', {
            templateUrl: '/static/views/login/login.html',
            controller: 'LoginController',
            auth: 'no'
        }).when('/dashboard', {
            templateUrl: '/static/views/dashboard/dashboard.html',
            controller: 'DashboardController',
            auth: 'yes'
        }).when('/analyze-tweets', {
            templateUrl: '/static/views/analyze-tweets/analyze-tweets.html',
            controller: 'AnalyzeTweetsController',
            auth: 'yes'
        }).when('/time-evaluation', {
            templateUrl: '/static/views/time-evaluation/time-evaluation.html',
            controller: 'TimeEvaluationController',
            auth: 'yes'
        }).when('/topic-analysis', {
            templateUrl: '/static/views/topic-analysis/topic-analysis.html',
            controller: 'TopicAnalysisController',
            auth: 'yes'
        }).when('/event-analysis', {
            templateUrl: '/static/views/event-analysis/event-analysis.html',
            controller: 'EventAnalysisController',
            auth: 'yes'
        }).otherwise('/dashboard');
    }]);