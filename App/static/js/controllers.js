'use-strict'

/*
 * Controllers, factories and a Directive 
 * */

/* factories */
fontApp.factory('fontFamilies', ['$resource', function($resource) {
    return $resource('getfonts', {'page':0, 'letter':null, 'limit':15}, {
        get: {method:'GET', params:{page:0, letter:null, 'limit':15}}                                                                              
    });
}]);

fontApp.factory('filteredFonts', ['$resource', function($resource) {
    return $resource('getfilteredfonts', {'page':0, 'limit':15}, {
        get: {method:'GET', params:{page:0, 'limit':15}}                                                                              
    });
}]);

fontApp.factory('getSpecimen', ['$resource', function($resource) {
    return $resource('getspecimen/:fontid', {fontid:'@fontid'});
}]);

/* Controllers */
var fontList = angular.module('fontList', ['ngRoute']);

fontList.controller('fontController', 
    ['$scope', '$filter', 'fontFamilies', 'filteredFonts', function($scope, $filter, fontFamilies, filteredFonts) {
    $scope.currentPage = 0;
    $scope.limit = 15;
    $scope.filtered = false;
    $scope.optionsform = {
        'name':'asc',
        'category':['Sans_serif', 'Serif'],
        'weight':'400',
        'style':['normal', 'italic'],
        'subset':['latin', 'latin-ext', 'menu'],
        'designer':'asc',
        'license': null,
        'limit':$scope.limit,
        'page':$scope.currentPage
    };

    var defaultFormOptions = $scope.optionsform;
    $scope.fontlist = fontFamilies.get({'page':$scope.currentPage, 'limit':$scope.limit});
    
    $scope.changePage = function(action) {
        if (action==='next') { 
            $scope.currentPage++; 
        } else if (action==='prev' && $scope.currentPage) {
            $scope.currentPage--;
        };
        if ($scope.filtered) {
            $scope.optionsform.limit = $scope.limit;
            $scope.optionsform.page = $scope.currentPage;
            $scope.fontlist = filteredFonts.get($scope.optionsform);
        } else {
            $scope.fontlist = fontFamilies.get({'page':$scope.currentPage, 'limit':$scope.limit, 'letter':$scope.letter});
        }
    };

    $scope.backToStart = function() {
        $scope.currentPage = 0;
        if ($scope.filtered) {
            $scope.optionsform.limit = $scope.limit;
            $scope.optionsform.page = $scope.currentPage;
            $scope.fontlist = filteredFonts.get($scope.optionsform);
        } else {
            $scope.fontlist = fontFamilies.get({'page':0, 'limit':$scope.limit, 'letter':$scope.letter});
        };
    };

    $scope.getFontsByLetter = function(eve) {
        $scope.letter = eve.target.id;
        $scope.currentPage = 0;
        $scope.filtered = false;
        $scope.optionsform = defaultFormOptions;
        $scope.fontlist = fontFamilies.get({'page':0, 'limit':$scope.limit,'letter':$scope.letter});
    };

    $scope.clearFilters = function() {
        $scope.filtered = false;
        $scope.optionsform = defaultFormOptions;
    };

    $scope.fontsByOptions = function(eve) {
        $scope.filtered = true;
        $scope.currentPage = 0;
        $scope.optionsform.limit = $scope.limit;
        $scope.optionsform.page = $scope.currentPage;
        $scope.fontlist = filteredFonts.get($scope.optionsform);
    };
}]);

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
