function drawCard(card, top_class){
    result = '' +
    '<div class="' + top_class  + (card.producible ? '' : ' unproducible-card') + '">' +
        '<div class="image-card" style="background-image: url(' + card.url + ');"></div>' +
        '<div class="image-frame" style="background-image: url(' + card.frame + ');"></div>' +
        '<div class="text-stat" id="card-size"' + (card.category === '캐릭터' ? ' style="display:none;"' : '')  + '>' + card.size + '</div>' +
        '<div class="text-stat" id="card-atk"' + (card.category === '추종자' ? '' : ' style="display:none;"') + '>' + card.atk + '</div>' +
        '<div class="text-stat" id="card-def"' + (card.category === '추종자' ? '' : ' style="display:none;"') + '>' + card.defs + '</div>' +
        '<div class="text-stat" id="card-hp"' + (card.category === '스펠' ? ' style="display:none;"' : '') + '>' + card.hp + '</div>' +
    '</div>'

    return result
}

function selectCard(id){
    $.ajax({
        url: '/card/select/' + id,
        type: 'GET',
        success: function(data) {
            const card = JSON.parse(data).selected_card;
            // console.log(data);
            document.getElementById('capture-btn').style.display = 'inline-block';
            $('.selected-card').html(
                drawCard(card, "selected-card-image") + 
                '<div class="selected-card-title">' +
                    '<div class="top-row">' +
                        '<p class="p-name">' + card.name + '</p>' +
                        '<div class="right-column">' +
                            '<p class="p-episode">' + card.episode + '</p>' +
                            '<p class="p-rarity">' + card.rarity + '</p>' +
                        '</div>' +
                    '</div>' +
                    '<p class="p-tag">' + card.tag + '</p>' +
                '</div>' +
                '<div class="selected-card-skill">' +
                    '<p class="p-skill">' + card.skill_turn + '</p>' +
                    '<p class="p-skill">' + card.skill_instance + '</p>' +
                    '<p class="p-skill">' + card.skill_attack + '</p>' +
                    '<p class="p-skill">' + card.skill_defend + '</p>' +
                '</div>'
            );
        }
    });
}

function captureCard() {
    html2canvas(document.getElementById("capture-area")).then(function(canvas) {
        var img = canvas.toDataURL("image/png"); // 이미지로 변환
        var link = document.createElement("a"); // 다운로드 링크 생성
        link.href = img; // 링크에 이미지 주소 설정
        link.download = "capture.png"; // 다운로드 파일명 설정
        link.click(); // 링크 클릭
    });
}

function updatePage(mode) {
    if (mode == 0){
        page = Math.max(page - 1, 1);
    }else{
        page = page + 1;
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

function syncSearchText(){
    $('#search-filter-detail').on('input', function(e) {
        if (e.target.name === 'search_text') {
            $('#search-filter-episode input[name="search_text"]').val(e.target.value);
        }
    });
    
    $('#search-filter-episode').on('input', function(e) {
        if (e.target.name === 'search_text') {
            $('#search-filter-detail input[name="search_text"]').val(e.target.value);
        }
    });
}