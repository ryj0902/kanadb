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
            if (document.getElementsByClassName('selected-card-skill').length > 0) {
                swapTextTo('skill');
            }
            document.getElementById('capture-btn').style.display = 'inline-block';
            document.getElementById('swap-text-btn').style.display = 'inline-block';
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
                '</div>' + 
                '<div class="selected-card-story" style="display:none;">' +
                    '<p class="p-skill">' + card.desc + '</p>' +
                '</div>'
            );
        }
    });
}

function swapTextTo(mode) {
    var img = document.getElementById('swap-text-btn')

    if (mode === 'story') {
        document.getElementsByClassName('selected-card-skill')[0].style.display = 'none';
        document.getElementsByClassName('selected-card-story')[0].style.display = 'inline-block';
        img.src = img.src.replace('story%201', 'cardText');
        img.onclick = function() { swapTextTo('skill'); };
    } else {
        document.getElementsByClassName('selected-card-skill')[0].style.display = 'inline-block';
        document.getElementsByClassName('selected-card-story')[0].style.display = 'none';
        img.src = img.src.replace('cardText', 'story%201');
        img.onclick = function() { swapTextTo('story'); };
    }
}

function captureCard() {
    html2canvas(document.getElementById("capture-area")).then(function(canvas) {
        var img = canvas.toDataURL("image/png"); // 이미지로 변환
        var link = document.createElement("a"); // 다운로드 링크 생성
        link.href = img; // 링크에 이미지 주소 설정
        link.download = $('.selected-card-title .p-name').text();
        link.click(); // 링크 클릭
    });
}
