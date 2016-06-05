'use-strict';

var fontList = angular.module('fontList', ['ngRoute']);

fontList.controller('fontController', 
    ['$scope', '$filter', '$anchorScroll', 'fontFamilies', 'filteredFonts', 'fontlistService', 'fontNameSearch', 
    function($scope, $filter, $anchorScroll, fontFamilies, filteredFonts, fontlistService, fontNameSearch) {
    /* $scope state is maintained with the fontlistService */

    var updateScope = function(eve) {
        /* update $scope from values in fontlistService (saved state) */
        Object.keys(fontlistService).forEach(function(key, ind, arr) {
            if (fontlistService[key] && !fontlistService[key].call) {
                $scope[key] = fontlistService[key];
            } else if (!fontlistService[key]) {
                // keep null and undefined values
                $scope[key] = fontlistService[key];
            };
        });
    };

    var updateState = function(eve) {
        /* update saved state from scope */
        Object.keys($scope).forEach(function(key, ind, arr) {
            if ($scope[key] && !key.startsWith('$') && !$scope[key].call) {
                fontlistService[key] = $scope[key];
            } else if (!$scope[key]) {
                // keep undefined values
                fontlistService[key] = $scope[key];
            }
        });
    };

    // init scope properties
    if (fontlistService.fontlist) {
        if (fontlistService.fontlist.$resolved) {
            updateScope();
        };
    };

    defaultPageArgs = {
        filtered: false,
        nameFiltered: false,
        page: 0,
        limit: 15,
        };

    if (!$scope.fontlist) {
        $scope.fontlist = fontFamilies.get(); 
        $scope.pageArgs = defaultPageArgs;
        updateState();
    };
    // scope properties setup
    

    $scope.changePage = function(action) {
        if (action==='next') { 
            $scope.pageArgs.page ++;
        } else if (action==='prev' && $scope.pageArgs.page) {
            $scope.pageArgs.page --;
        };

        // there needs to be a way better routing system here
        if ($scope.pageArgs.filtered) {
            $scope.fontlist = filteredFonts.get($scope.pageArgs);
        } else if ($scope.pageArgs.nameFiltered) {
            $scope.fontlist = fontNameSearch.get($scope.pageArgs);
        } else {
            $scope.fontlist = fontFamilies.get($scope.pageArgs);
        };

        updateState();
        $anchorScroll(0);
    };

    $scope.getFontsByLetter = function(eve) {
        // set defaultPageArgs to default values
        Object.keys(defaultPageArgs).forEach((k) => $scope.pageArgs[k] = defaultPageArgs[k]);
        $scope.pageArgs.letter = eve.target.id;
        $scope.fontlist = fontFamilies.get($scope.pageArgs);
        updateState();
        $anchorScroll(0);
    };

    $scope.backToStart = function() {
        $scope.pageArgs.page = 0;

        if ($scope.pageArgs.filtered) {
            $scope.fontlist = filteredFonts.get($scope.pageArgs);
        } else {
            $scope.fontlist = fontFamilies.get($scope.pageArgs);
        };

        updateState();
        $anchorScroll(0);
    };

    $scope.clearFilters = function() {
        // set defaultPageArgs to default values
        Object.keys(defaultPageArgs).forEach((k) => $scope.pageArgs[k] = defaultPageArgs[k]);
        $scope.fontlist = fontFamilies.get($scope.pageArgs);
        updateState();
        $anchorScroll(0);
    };

    $scope.getFilteredFontlist = function(eve) {
        // set defaultPageArgs to default values
        Object.keys(defaultPageArgs).forEach((k) => $scope.pageArgs[k] = defaultPageArgs[k]);
        $scope.pageArgs.filtered = true;
        $scope.fontlist = filteredFonts.get($scope.pageArgs);
        updateState();
        $anchorScroll(0);
    };

    $scope.searchFontsByName = function() {
        // set defaultPageArgs to default values
        Object.keys(defaultPageArgs).forEach((k) => $scope.pageArgs[k] = defaultPageArgs[k]);
        $scope.pageArgs['nameFiltered'] = true;
        $scope.fontlist = fontNameSearch.get($scope.pageArgs);
        updateState();
        $anchorScroll(0);
    };
}]);
