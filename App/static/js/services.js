'use-strict'
/* Services and Resources */

fontApp.factory('fontFamilies', ['$resource', 'defaultPageArgs', function($resource, defaultPageArgs) {
    return $resource('getfonts', defaultPageArgs, {
            get: {method:'GET', defaultPageArgs}
    });
}]);

fontApp.factory('fontNameSearch', ['$resource', 'defaultPageArgs', function($resource, defaultPageArgs) {
    return $resource('searchFontsByName', defaultPageArgs, {
        get: {method:'GET', defaultPageArgs}
    });
}]);

fontApp.factory('filteredFonts', ['$resource', 'defaultPageArgs', function($resource, defaultPageArgs) {
    var filterParams = {
        'name':'asc',
        'category':null,
        'weight':null,
        'style':null,
        'subset':null,
        'designer':'asc',
        'license': null
    };
    Object.keys(defaultPageArgs).forEach((key) => filterParams[key] = defaultPageArgs[key]);

    return $resource('getfilteredfonts', filterParams, {
        get: {method:'GET', params: filterParams}                                                                              
    });
}]);

fontApp.factory('getSpecimen', ['$resource', function($resource) {
    return $resource('getspecimen/:fontid', {fontid:'@fontid'});
}]);

fontApp.factory('fontlistService', function() {
    /* this is where saved state is kept */
    return {};
});
