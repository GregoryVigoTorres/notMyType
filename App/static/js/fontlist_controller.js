'use-strict';

var fontList = angular.module('fontList', ['ngRoute']);

fontList.controller('fontController', 
    ['$scope', '$filter', '$anchorScroll', 'fontFamilies', 'filteredFonts', 'fontlistService', 'fontNameSearch', 'defaultPageArgs', 
    function($scope, $filter, $anchorScroll, fontFamilies, filteredFonts, fontlistService, fontNameSearch, defaultPageArgs) {
    /* $scope state is maintained with the fontlistService 
     * don't just copy defaultPageArgs
     * because the original values will get overwritten
     * */

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

    var resetPageArgs = function(reqArgs) {
        // this sets values defined in defaultPageArgs
        if (!$scope.pageArgs) { $scope.pageArgs = {} };

        Object.keys($scope.pageArgs).forEach(function(key) {
            if (reqArgs) {
                // keep properties in reqArgs
                if (reqArgs.indexOf(key) < 0) {
                    delete $scope.pageArgs[key];
                };
            };
        });

        Object.keys(defaultPageArgs).forEach((k) => $scope.pageArgs[k] = defaultPageArgs[k]);
    };

    // init scope properties
    if (fontlistService.fontlist) {
        if (fontlistService.fontlist.$resolved) {
            updateScope();
            this.currentFontListSource = fontFamilies;
        };
    };

    if (!$scope.fontlist) {
        resetPageArgs();
        $scope.fontlist = fontFamilies.get($scope.pageArgs); 
        updateState();
    };
    // scope properties setup

    $scope.changePage = function(action) {
        if (action==='next') { 
            $scope.pageArgs.page ++;
        } else if (action==='prev' && $scope.pageArgs.page) {
            $scope.pageArgs.page --;
        };

        if (!this.currentFontListSource) {
            // this is needed because sometimes this is empty
            this.currentFontListSource = fontFamilies;
        };

        $scope.fontlist = this.currentFontListSource.get($scope.pageArgs);
        updateState();
        $anchorScroll(0);
    };

    $scope.getFontsByLetter = function(eve) {
        resetPageArgs(['letter']);
        $scope.pageArgs.letter = eve.target.id;
        this.currentFontListSource = fontFamilies;

        $scope.fontlist = fontFamilies.get($scope.pageArgs);
        updateState();
        $anchorScroll(0);
    };

    $scope.backToStart = function() {
        $scope.pageArgs.page = 0;
        $scope.fontlist = this.currentFontListSource.get($scope.pageArgs);
        updateState();
        $anchorScroll(0);
    };

    $scope.clearFilters = function() {
        resetPageArgs();
        this.currentFontListSource = fontFamilies;
        $scope.pageArgs.filtered = false;
        $scope.fontlist = fontFamilies.get($scope.pageArgs);
        updateState();
        $anchorScroll(0);
    };

    $scope.getFilteredFontlist = function(eve) {
        resetPageArgs(['name', 'designer', 'subset', 'category', 'license', 'weight', 'style', 'filtered']);
        $scope.pageArgs.filtered = true;
        this.currentFontListSource = filteredFonts;
        $scope.fontlist = filteredFonts.get($scope.pageArgs);
        updateState();
        $anchorScroll(0);
    };

    $scope.searchFontsByName = function() {
        resetPageArgs(['nameSearchTerm']);
        this.currentFontListSource = fontNameSearch;
        $scope.fontlist = fontNameSearch.get($scope.pageArgs);
        updateState();
        $anchorScroll(0);
    };
}]);
