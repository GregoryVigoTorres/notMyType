'use-strict'

var fontApp = angular.module('fontApp', ['ngRoute', 'ngResource', 'ngSanitize', 'fontList', 'gSpecimen']);

fontApp.config(['$routeProvider', function($routeProvider) {
    $routeProvider.when(
                '/', {
                templateUrl: '/static/partials/fontlist.html',
                controller: 'fontController'
            }).when(
                '/specimen/:fontid', {
                templateUrl: '/static/partials/specimen.html',
                controller: 'specimenCtrl'
    });
}]);

// this is used in services and controller, 
// it should be defined ONCE here.
// Be VERY careful about changing its values.
fontApp.value(
        'defaultPageArgs', {
        page: 0,
        limit: 15,
        letter: null,
        });
