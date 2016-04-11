'use-strict'
/* Services and Resources */
fontApp.factory('fontFamilies', ['$resource', function($resource) {
    return $resource('getfonts', {'page':0, 'letter':null, 'limit':15}, {
        get: {method:'GET', params:{page:0, letter:null, 'limit':15}}                                                                              
    });
}]);

fontApp.factory('filteredFonts', ['$resource', function($resource) {
    var defaultFormOptions = {
        'name':'asc',
        'category':['Sans_serif', 'Serif'],
        'weight':'400',
        'style':['normal', 'italic'],
        'subset':['latin', 'latin-ext', 'menu'],
        'designer':'asc',
        'license': null,
        'limit': 15,
        'page':0
    };
    return $resource('getfilteredfonts', defaultFormOptions, {
        get: {method:'GET', params: defaultFormOptions}                                                                              
    });
}]);

fontApp.factory('getSpecimen', ['$resource', function($resource) {
    return $resource('getspecimen/:fontid', {fontid:'@fontid'});
}]);

fontApp.factory('fontlistService', function() {
    /* this is where saved state is kept */
    return {};
});
