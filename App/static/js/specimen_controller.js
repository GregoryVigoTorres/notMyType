'use-strict';

var gSpecimen = angular.module('gSpecimen', ['ngRoute', 'ngSanitize', 'ngResource']);

gSpecimen.filter('strReplace', 
        function() {
            return function(str, substr, newsubstr) {
                var replRe = new RegExp(substr, 'g');
                return str.replace(replRe, newsubstr);
        };
});

gSpecimen.controller('specimenCtrl', 
    ['$scope', '$route', '$location', '$anchorScroll', '$filter', '$window', 'getSpecimen', 
    function($scope, $route, $location, $anchorScroll, $filter, $window, getSpecimen) {
        $scope.chardata = getSpecimen.get($route.current.params);

        $scope.navVisible = false;
        $scope.toggleNavVisible = function(eve) {
            $scope.navVisible = !$scope.navVisible;
            $anchorScroll(0);
        };

        $scope.scrollToBlock = function(name) {
            var hash = $filter('strReplace')(name, ' ', '-');
            $anchorScroll(hash);
            $scope.navVisible = false;
        };

        $scope.showBackToTop=false;
        /* show the "top" button */
        $window.onscroll = function() {
            if ($window.scrollY > 800 && !$scope.showBackToTop) { 
                /* prevent apply from getting called too often */
                $scope.showBackToTop=true;
                $scope.$apply();
            } else if ($window.scrollY < 800 && $scope.showBackToTop) {
                $scope.showBackToTop=false;
                $scope.$apply();
            } 
        };

        $scope.scrollToTop = function() {
            $scope.showBackToTop=false;
            $anchorScroll(0);
        };
}]);

gSpecimen.directive('lipsum', function() {
    return {
        restrict: 'E',
        templateUrl: '/static/partials/lipsum.html'
    }
});

gSpecimen.controller('lipsumController', ['$scope', '$anchorScroll', '$filter', 
function($scope, $anchorScroll, $filter) {
    $scope.lipsumVisible = false;
    $scope.lipsumMsg = 'show';
    $scope.lipsumSize = 1;

    $scope.toggleLipsumVisible = function(eve) {
        $scope.lipsumVisible = !$scope.lipsumVisible;
        if ($scope.lipsumVisible) {
            $scope.lipsumMsg = 'hide';
            $anchorScroll(0);
        } else {
            $scope.lipsumMsg = 'show';
        }
    };

    $scope.invertLipsumColors = function(eve) {
        if (!$scope.lipsumColors) {
            $scope.lipsumColors = 'dark-on-light'
        } else {
            $scope.lipsumColors = undefined;
        };
    };

    $scope.resetLipsum = function(eve) {
        $scope.lipsumColors = undefined;
        $scope.lipsumSize = 1;
    };

    $scope.$watch('chardata.entities', function() {
        if ($scope.chardata.entities) {
            $scope.uniRangeNames = {};
            $scope.punc = {};

            $scope.chardata.entities.forEach(function(ent) {
                ent.cats.forEach(function(cat) { 
                    if (cat.name.includes('Letter') && cat.chars.length > 20) {
                        $scope.uniRangeNames[ent.name] = true;
                    };

                    if (cat.name.includes('Punctuation')) {
                        cat.chars.forEach(function(ch) {
                            if (!$scope.punc[ch.block]) {
                                $scope.punc[ch.block] = [];
                            };
                            $scope.punc[ch.block].push(ch.cp);
                        }); //chars.forEach
                    }; // if Punctuation
                    
                    if (cat.name.includes('Currency')) {
                        cat.chars.forEach(function(ch) {
                            if (!$scope.punc[ch.block]) {
                                $scope.punc[ch.block] = [];
                            };
                            $scope.punc[ch.block].push(ch.cp);
                        }); //chars.forEach
                    }; // if Currency

                }); // cats.forEach
            }); // entities.forEach
        }; // if entities
    }); // scope.watch
}]);
