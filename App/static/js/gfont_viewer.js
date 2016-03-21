function Controller() {
    this.setupEventHandlers();
};

Controller.prototype.setupEventHandlers = function() {
    /* this is really an init function 
     * these event handlers should only be bound when the page loads for the first time
     * */
    $('#next').on('click', this.changeFontPage.bind(this));  
    $('#prev').on('click', this.changeFontPage.bind(this));  
    $('#fonts-by-letter li span').on('click', this.getFontsByLetter.bind(this));
    this.keepaliveEventHandlers();
    // $(document).ajaxSuccess(this.keepaliveEventHandlers.bind(this));
};

Controller.prototype.keepaliveEventHandlers = function() {
    /* Some things always need to get (re)bound to the same event handler
     * when new content is loaded into the main container
     * this gets called on ajax.success
     * */
    $('body #main-container .font-list li > a').on('click', this.getFontSpecimen.bind(this));
};

Controller.prototype.closeSpecimenView = function(eve) {
    $(this.lastView).replaceAll('#main-container');
    console.log(this.letter);
    if (this.letter) {
        $('#next').on('click', this.changeFontPageByLetter.bind(this));  
        $('#prev').on('click', this.changeFontPageByLetter.bind(this));  
        this.keepaliveEventHandlers();
    } else {
        this.setupEventHandlers();
    }
};

Controller.prototype.getFontSpecimen = function(eve) {
    /* also get a lot more font data */
    eve.preventDefault();
    var url = eve.currentTarget.href;
    $.ajax({
        'url':url,
        'contentType':'text/plain',
        'dataType':'html',
        'complete': (jqXhr, status) => {
            this.keepaliveEventHandlers();
            $('#close-specimen').on('click', this.closeSpecimenView.bind(this));
        },
        'success': (data, status, jqXhr) => {
            this.lastView = $('#main-container').replaceWith(data);
            window.scrollTo(0, 0);
            $('#center-col').addClass('specimen-view');

        },
    });
};

Controller.prototype.getFontsByLetter = function(eve) {
    var letter = eve.currentTarget.id;
    this.currentLetter = letter;

    $.ajax({
        'url':'/fontsbyletter/'+letter,
        'contentType':'text/plain',
        'dataType':'html',
        'success': (data, status, jqXhr) => {
            $(data).replaceAll('#main-container');
            window.scrollTo(0, 0);
        },
        'complete': (jqXhr, status) => {
            $('#next').on('click', this.changeFontPageByLetter.bind(this));  
            $('#prev').on('click', this.changeFontPageByLetter.bind(this));  
            this.keepaliveEventHandlers();
        },
    });
};

Controller.prototype.changeFontPageByLetter = function(eve) {
    /*  Prev/next when in fonts by letter view
     *  this repeats a lot of functionality in ANOTHER function... 
     *  they should both be refactored later, probably
     * */

    if (eve.currentTarget.id === 'next') {
        var offset = eve.currentTarget.dataset.next_offset;
    } else {
        var offset = eve.currentTarget.dataset.prev_offset;
    };

    var url = `/fontsbyletter/${this.currentLetter}/${offset}`;

    $.ajax({'url':url,
            'contentType':'text/plain',
            'dataType':'html',
            'success': (data, status, jqXhr) => {
                $(data).replaceAll('#main-container');
                window.scrollTo(0, 0);
            },
            'complete': (jqXhr, status) => {
                $('#next').on('click', this.changeFontPageByLetter.bind(this));  
                $('#prev').on('click', this.changeFontPageByLetter.bind(this));  
                this.keepaliveEventHandlers();
            },
        });
};

Controller.prototype.changeFontPage = function(eve) {
    /* prev/next when not in fonts by letter view */
    if (eve.currentTarget.id === 'next') {
        var offset = eve.currentTarget.dataset.next_offset;
    } else {
        var offset = eve.currentTarget.dataset.prev_offset;
    };

    $.ajax({'url':'/getfonts/'+offset,
            'contentType':'text/plain',
            'dataType':'html',
            'success': (data, status, jqXhr) => {
                $(data).replaceAll('#main-container');
                window.scrollTo(0, 0);
            },
            'complete': (jqXhr, status) => {
                this.setupEventHandlers();
                this.keepaliveEventHandlers();
            },
        });
};

(function() {
    'use-strict';
    function instance() {
        return new Controller();  
    };
    instance();
})();
