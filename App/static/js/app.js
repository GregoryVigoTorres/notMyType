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
