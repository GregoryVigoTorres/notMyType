/* Jasmin tests to be used with karma
 */

describe("fontlist tests", function() {
    beforeEach(module("fontApp"));

    var $controller, fontFamilies, filteredFonts, $httpBackend;

    beforeEach(inject(function(_$controller_, _fontFamilies_, _filteredFonts_, _$httpBackend_, $injector) { 
        $controller = _$controller_;
        $httpBackend = _$httpBackend_;
        fontFamilies = _fontFamilies_;
        filteredFonts = _filteredFonts_;
    }));

    describe("fontList spec", function() {
        var $scope, controller;

        beforeEach(function()  {
            /* this makes controller & $scope available in these tests */
            $scope = {};
            controller = $controller('fontController', {$scope: $scope});

            // url = "getfonts?filtered=false&limit=15&page=0";
            url = "getfonts?limit=15&page=0";
            $httpBackend.whenGET(url).respond(200, 
                    {
                        'fontcount':80, 
                        'fontdata':[{}, {}, {}],
                        'fontscss':'@font-family:'
                    });
            $httpBackend.whenGET("/static/partials/fontlist.html").respond(200, '');
        });

       afterEach(function() {
            $httpBackend.flush();
            $httpBackend.verifyNoOutstandingExpectation();
            $httpBackend.verifyNoOutstandingRequest();
       });

        it("fontList pageArgs", inject(function() {
            expect($scope.pageArgs).toBeDefined();
        }));
       
       it('service should respond', inject(function(fontFamilies) {
            req = fontFamilies.get($scope.pageArgs);
            req.$promise.then(function(response) { 
                expect(response.fontcount).toBeDefined();
                expect(response.fontdata).toBeDefined();
                expect(response.fontscss).toBeDefined();
            });
       }));

        /* services */
        it("expects fontsByLetter to return something", inject(function() {
            url = "getfonts?letter=a&limit=15&page=0";
            $httpBackend.whenGET(url).respond(200, 
                    {
                        'fontcount':80, 
                        'fontdata':[{}, {}, {}],
                        'fontscss':'@font-family:'
                    });

            $scope.pageArgs.letter = 'a';
            req = fontFamilies.get($scope.pageArgs);
            req.$promise.then(function(response) { 
                expect(response.fontcount).toBeDefined();
                expect(response.fontdata).toBeDefined();
                expect(response.fontscss).toBeDefined();
            });
        }));

        it("expects filteredFonts to work", inject(function() {
            /* these are default values from the service
              */
            url = "getfilteredfonts?"+
                "category=Sans_serif&category=Serif&"+
                "designer=asc&"+
                "filtered=true&"+
                "limit=15&"+
                "name=asc&"+
                "page=0&"+
                "style=italic&"+
                "subset=latin&subset=latin-ext&subset=menu&"+
                "weight=400";

            $scope.pageArgs.filtered = false;
            $scope.pageArgs.category = ['Sans_serif','Serif'];
            $scope.pageArgs.designer = 'asc';
            $scope.pageArgs.filtered = true;
            $scope.pageArgs.limit = 15;
            $scope.pageArgs.name = 'asc';
            $scope.pageArgs.page = 0;
            $scope.pageArgs.style = ['italic',];
            $scope.pageArgs.subset = ['latin', 'latin-ext', 'menu'];
            $scope.pageArgs.weight = 400;

            $httpBackend.whenGET(url).respond(200, 
                    {
                        'fontcount':80, 
                        'fontdata':[{}, {}, {}],
                        'fontscss':'@font-family:'
                    });

            req = filteredFonts.get($scope.pageArgs);
            req.$promise.then(function(response) { 
                expect(response.fontcount).toBeDefined();
                expect(response.fontdata).toBeDefined();
                expect(response.fontscss).toBeDefined();
            });
        }));

        it("fontList backToStart", inject(function() {
            $scope.backToStart();
            expect($scope.fontlist).toBeDefined();
        }));

        it("fontList changePage", inject(function() {
            $scope.changePage();
            expect($scope.fontlist).toBeDefined();
        }));
    });
});

