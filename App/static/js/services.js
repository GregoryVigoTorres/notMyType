'use-strict'
/* Services and Resources */
fontApp.factory('fontFamilies', ['$resource', function($resource) {
    return $resource('getfonts', {'filtered':false, 'page':0, 'letter':null, 'limit':15}, {
        get: {method:'GET', params:{filtered:false, page:0, letter:null, 'limit':15}}                                                                              
    });
}]);

fontApp.factory('filteredFonts', ['$resource', function($resource) {
    var defaultParams = {
        'name':'asc',
        'category':null,
        'weight':null,
        'style':null,
        'subset':null,
        'designer':'asc',
        'license': null,
        'limit': 15,
        'page':0
    };
    return $resource('getfilteredfonts', defaultParams, {
        get: {method:'GET', params: defaultParams}                                                                              
    });
}]);

fontApp.factory('getSpecimen', ['$resource', function($resource) {
    return $resource('getspecimen/:fontid', {fontid:'@fontid'});
}]);

fontApp.factory('fontlistService', function() {
    /* this is where saved state is kept */
    return {};
});
