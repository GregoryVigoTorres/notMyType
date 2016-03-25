'use-strict'

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
        $scope.letter = eve.srcElement.id;
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
        $scope.nav_visible = false;
        $scope.show_all_in_family = false;
        $scope.show_unicode_blocs = false;
        $scope.copyright_visible = false;

        $scope.toggleNav = function(eve) {
            $scope.nav_visible = !$scope.nav_visible;
        };

        $scope.closeNav = function() {
            $scope.nav_visible = false;
        };

        $scope.showAllFonts = function() {
            $scope.show_all_in_family = !$scope.show_all_in_family;
        };

        $scope.showUnicodeBlocks = function() {
            $scope.show_unicode_blocks = !$scope.show_unicode_blocks;
        };

        $scope.showCopyright = function() {
            $scope.copyright_visible = !$scope.copyright_visible;
        };

        $scope.scrollToBlock = function(name) {
            var hash = $filter('strReplace')(name, ' ', '-');
            $anchorScroll(hash);
            $scope.nav_visible = false;
        };

        $scope.showBackToTop=false;
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
