function updatePage(mode) {
    if (mode == 0){
        page = Math.max(page - 1, 1);
    }else{
        page = Math.min(page + 1, page_total);
    }

    // 현재 URL에 적용된 검색 조건으로 다음 페이지를 가져온다
    const params = new URLSearchParams(window.location.search);
    params.set('page', page);

    $.ajax({
        url: baseUrl + '/' + lang + '/card/?' + params.toString(),
        type: 'GET',
        success: function(response) {
            var $response = $(response);
            var $imageGrid = $response.find('.image-grid');
            
            $('.image-grid').html($imageGrid.html());
        }
    });
    $('.page').html(page + ' / ' + page_total);
}

function openTab(tabName) {
    var i, tabcontent, tablinks;
    tabcontent = $(".search-filter");
    for (i = 0; i < tabcontent.length; i++) {
        tabcontent[i].style.display = "none";
    }
    tablinks = $(".search-btn");
    for (i = 0; i < tablinks.length; i++) {
        tablinks[i].className = tablinks[i].className.replace(" active", "");
    }
    $("#search-filter-"+tabName)[0].style.display = "block";
    $("#btn-"+tabName)[0].className += " active";

    // change all submit button's value to current tab 
    let buttons = document.getElementsByClassName("btn-submit");
    for (var i = 0; i < buttons.length; i++) {
        buttons[i].value = tabName;
    }

    tab = tabName;
}

function syncSearchFilter(){
    // search
    $('#search-filter-detail, #search-filter-episode, #search-filter-etc').on('input change', function(e) {
        if (e.target.name === 'search_text' || e.target.name === 'search_type') {
            $('#search-filter-detail input[name="' + e.target.name + '"], #search-filter-detail select[name="' + e.target.name + '"]').val(e.target.value);
            $('#search-filter-episode input[name="' + e.target.name + '"], #search-filter-episode select[name="' + e.target.name + '"]').val(e.target.value);
            $('#search-filter-etc input[name="' + e.target.name + '"], #search-filter-etc select[name="' + e.target.name + '"]').val(e.target.value);
        }
    });
}

function addToggleAllEventListener(){
    const toggleItems = [
        { toggleId: 'toggle-all-episode-season1', name: 'episode_season1' },
        { toggleId: 'toggle-all-episode-season2', name: 'episode_season2' },
        { toggleId: 'toggle-all-episode-season3', name: 'episode_season3' },
        { toggleId: 'toggle-all-episode-event', name: 'episode_event' },
        { toggleId: 'toggle-all-episode-extra', name: 'episode_extra' },
        { toggleId: 'toggle-all-category', name: 'category' },
        { toggleId: 'toggle-all-rarity', name: 'rarity' },
        { toggleId: 'toggle-all-theme', name: 'theme' }
    ];

    toggleItems.forEach(item => {
        const toggleElem = document.getElementById(item.toggleId);
        if (toggleElem) {
            toggleElem.addEventListener('click', function() {
                let checkboxes = document.querySelectorAll(`input[name="${item.name}"]`);
                let isChecked = this.checked;
                checkboxes.forEach(function(checkbox) {
                    checkbox.checked = isChecked;
                });
            });
        }
    });
}