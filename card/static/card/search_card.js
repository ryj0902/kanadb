function updatePage(mode) {
    if (mode == 0){
        page = Math.max(page - 1, 1);
    }else{
        page = Math.min(page + 1, page_total);
    }

    var form = document.getElementById('search-form');
    var formData = new FormData(form);
    // Serialize the form data to JSON
    var serializedData = {};
    for (var [key, value] of formData.entries()) {
        if(!(key in serializedData)){
            serializedData[key] = [value];
        }else if(key === 'search_text' || key === 'search_type'){
            continue;
        }else{
            serializedData[key].push(value);
        }
    }
    serializedData['page'] = page
    // console.log(serializedData)

    $.ajax({
        url: '/card/',
        type: 'POST',
        data: serializedData,
        traditional: true,
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

    tab = tabName;
}

function syncSearchFilter(){
    // search
    $('#search-filter-detail, #search-filter-episode').on('input change', function(e) {
        if (e.target.name === 'search_text' || e.target.name === 'search_type') {
            $('#search-filter-detail input[name="' + e.target.name + '"], #search-filter-detail select[name="' + e.target.name + '"]').val(e.target.value);
            $('#search-filter-episode input[name="' + e.target.name + '"], #search-filter-episode select[name="' + e.target.name + '"]').val(e.target.value);
        }
    });
}