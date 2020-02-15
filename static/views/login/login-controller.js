/**
 * Created by buwan on 7/6/2017.
 */
app.controller('LoginController', function LoginController($scope, $sessionStorage, $http, $rootScope, $location) {
    $scope.login = {
        username: "",
        password: ""
    };

    $scope.doLogin = function () {
        $location.url('/dashboard');
    };
});