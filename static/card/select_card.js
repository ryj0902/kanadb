function drawCard(card, className){
    let name = (lang == 'ko') ? card.name : card.name_us;
    let tag = (lang == 'ko') ? card.tag : card.tag_us;
    let skill_turn = (lang == 'ko') ? card.skill_turn : card.skill_turn_us;
    let skill_instance = (lang == 'ko') ? card.skill_instance : card.skill_instance_us;
    let skill_attack = (lang == 'ko') ? card.skill_attack : card.skill_attack_us;
    let skill_defend = (lang == 'ko') ? card.skill_defend : card.skill_defend_us;
    let desc = (lang == 'ko') ? card.desc : card.desc_us;

    let character = (lang == 'ko') ? '캐릭터' : 'Character';
    let spell = (lang == 'ko') ? '스펠' : 'Spell';
    let follower = (lang == 'ko') ? '추종자' : 'Follower';

    const button = document.getElementById('vert-horz-btn');
    const currentText = button.textContent.trim();
    const vert_horz = currentText === horizontalLayout ? 'vert': 'horz' 

    console.log(card);
    result = '' +
    '<div class="' + className + '-image'  + (card.producible ? '' : ' unproducible-card') + '">' +
        '<div class="image-card" style="background-image: url(' + card.url + ');"></div>' +
        '<div class="image-frame" style="background-image: url(' + card.frame + ');"></div>' +
        '<div class="text-stat" id="card-size"' + (card.category === character ? ' style="display:none;"' : '')  + '>' + card.size + '</div>' +
        '<div class="text-stat" id="card-atk"' + (card.category === follower ? '' : ' style="display:none;"') + '>' + card.atk + '</div>' +
        '<div class="text-stat" id="card-def"' + (card.category === follower ? '' : ' style="display:none;"') + '>' + card.defs + '</div>' +
        '<div class="text-stat" id="card-hp"' + (card.category === spell ? ' style="display:none;"' : '') + '>' + card.hp + '</div>' +
        '<div class="image-enhance" style="background-image: url(' + card.frame_enh + ');' + (card.enhance === 0 ? ' display:none;"' : '') + '"></div>' +
        '<div class="text-stat" id="card-enhance"' + (card.enhance === 0 ? ' style="display:none;"' : '') + '>' + card.enhance + '</div>' +
    '</div>' +
    '<div class="selected-card-texts">' +
        '<div class="' + className + '-title">' +
            '<div class="top-row">' +
                '<p class="p-name">' + name + '</p>' +
                '<div class="right-column">' +
                    '<p class="p-episode">' + card.episode + '</p>' +
                    '<p class="p-rarity">' + card.rarity + '</p>' +
                '</div>' +
            '</div>' +
            '<p class="p-tag">' + tag + '</p>' +
        '</div>' + 
        '<div class="' + className + '-skill">' +
            '<p class="p-skill">' + skill_turn + '</p>' +
            '<p class="p-skill">' + skill_instance + '</p>' +
            '<p class="p-skill">' + skill_attack + '</p>' +
            '<p class="p-skill">' + skill_defend + '</p>' +
        '</div>' + 
        '<div class="' + className + '-story" style="display:none;">' +
            '<p class="p-skill">' + desc + '</p>' +
        '</div>' +
    '</div>'

    return result
}

function selectCard(id, init_link){
    $.ajax({
        url: baseUrl + '/' + lang + '/card/select/' + id,
        type: 'GET',
        success: function(data) {
            const card = JSON.parse(data).selected_card;
            // console.log(data);
            if (document.getElementsByClassName('selected-card-skill').length > 0) {
                swapTextTo('skill');
            }
            document.getElementById('capture-btn').style.display = 'inline-block';
            document.getElementById('vert-horz-btn').style.display = 'inline-block';
            document.getElementById('swap-text-btn').style.display = 'inline-block';

            if (Number(init_link) === 0) { // activate link button
                link_origin_id = card.id;
                document.getElementById('card-link-btn').style.display = 'inline-block';
                if (card.link === "-1") {
                    document.getElementById('card-link-btn').classList.add('grayscale');
                } else {
                    document.getElementById('card-link-btn').classList.remove('grayscale');
                }
                document.getElementById('card-link-prev').style.display = 'none';
                document.getElementById('card-link-reset').style.display = 'none';
                document.getElementById('card-link-next').style.display = 'none';
                link_card_ids = card.link;
            }

            if (card.category === '추종자' || card.category === 'Follower') {
                document.getElementById('card-enhance-img').style.display = 'inline-block';
                document.getElementById('card-enhance-down').style.display = 'inline-block';
                document.getElementById('card-enhance-up').style.display = 'inline-block';

                enhance_card_prev = card.enh_prev;
                enhance_card_next = card.enh_next;
                if (enhance_card_prev === -1) {
                    enhance_origin_id = card.id;
                }
                document.getElementById('card-enhance-down').style.opacity = (enhance_card_prev === -1) ? 0.5 : 1.0;
                document.getElementById('card-enhance-up').style.opacity = (enhance_card_next === -1) ? 0.5 : 1.0;
            } else {
                document.getElementById('card-enhance-img').style.display = 'none';
                document.getElementById('card-enhance-down').style.display = 'none';
                document.getElementById('card-enhance-up').style.display = 'none';
            }

            $('.selected-card').html(
                drawCard(card, "selected-card")
            );
        }
    });
}

function swapTextTo(mode) {
    var img = document.getElementById('swap-text-btn');

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
        var imageName = $('.selected-card-title .p-name').text();
        link.download = `${imageName}.${'png'}`
        link.click(); // 링크 클릭
    });
}

function showLinkCard(offset) {
    // console.log(link_card_ids, link_card_idx, offset);
    // no link card exist
    if (link_card_ids === '-1') { 
        return
    }
    // this is first link card, so previous does not exist
    if (link_card_idx === 0 && offset === -1) { 
        return
    }
    let cardIds = link_card_ids.split(',')
    // this is last link card, so next does not exist
    if (link_card_idx + offset === cardIds.length ) { 
        return
    }
    link_card_idx += offset;
    let cardId = parseInt(cardIds[link_card_idx]);
    document.getElementById('card-link-prev').style.opacity = link_card_idx === 0 ? 0.5 : 1.0;
    document.getElementById('card-link-next').style.opacity = link_card_idx + 1 < cardIds.length ? 1.0 : 0.5;
    selectCard(cardId, 1);

    document.getElementById('card-link-btn').style.display = 'none';
    document.getElementById('card-link-prev').style.display = 'inline-block';
    document.getElementById('card-link-reset').style.display = 'inline-block';
    document.getElementById('card-link-next').style.display = 'inline-block';
}

function resetLinkCard() {
    selectCard(link_origin_id, 0);
    link_card_idx = 0;
}

function showEnhanceCard(offset) {
    if (enhance_card_prev === -1 && offset === -1) { 
        return
    }
    if (enhance_card_next === -1 && offset === 1) { 
        return
    }

    let cardId = (offset === -1) ? enhance_card_prev : enhance_card_next;
    selectCard(cardId, 1);
}

function resetEnhanceCard() {
    selectCard(enhance_origin_id, 1);
}

const changeLayoutClass = ['right', 'selected-card', 'selected-card-side']
const changeLayoutId = ['card-enhance-img', 'card-enhance-up', 'card-enhance-down',
                        'card-link-btn', 'card-link-prev', 'card-link-next', 'card-link-reset',
                        'swap-text-btn']
function verthorzCard() {
    const button = document.getElementById('vert-horz-btn');
    const currentText = button.textContent.trim();
    const vert_horz = currentText === horizontalLayout ? 'horz': 'vert' 

    changeLayoutClass.forEach(className => {
        const elements = document.querySelectorAll(`.${className}`);
        elements.forEach(element => {
            if (vert_horz === 'horz') {
                element.classList.add('horz-layout');
            } else {
                element.classList.remove('horz-layout');
            }
            // element.classList.remove(vert_horz === 'horz' ? 'vert-layout' : 'horz-layout');
            // element.classList.add(vert_horz === 'horz' ? 'horz-layout' : 'vert-layout');
        });
      });
    
    button.textContent = vert_horz === 'horz' ? verticalLayout : horizontalLayout;
}