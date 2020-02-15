/**
 * Created by buwan on 7/6/2017.
 */
app.controller('DashboardController', function DashboardController($scope, $sessionStorage, $http, $location) {
    $scope.changeView = function (id) {
        $location.url('/' + id);
    };
});