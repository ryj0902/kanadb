function showEdit() {
    document.getElementById("deck-edit").style.display = "flex";
    document.getElementById("deck-view").style.display = "none";
    document.getElementById("edit-button").classList.add("active");
    document.getElementById("view-button").classList.remove("active");
}

function showView() {
    document.getElementById("deck-edit").style.display = "none";
    document.getElementById("deck-view").style.display = "block";
    document.getElementById("edit-button").classList.remove("active");
    document.getElementById("view-button").classList.add("active");
}


let draggedCardId = null;
let draggedFromDeck = false; // 드래그가 덱 영역 내에서 시작했는지 여부
let isDragging = false; // 드래그 상태 추적

const deckPreview = document.getElementById('deck-preview-content');

// 마우스 좌표 추적
let mouseX = 0;
let mouseY = 0;
let isInsideDeck = false; // 덱 영역 내부에 있는지 확인

document.addEventListener('mousemove', (event) => {
    mouseX = event.clientX;
    mouseY = event.clientY;
});

document.addEventListener('dragover', (event) => {
    event.preventDefault(); // 드롭을 허용하기 위해 기본 동작 방지

    mouseX = event.clientX;
    mouseY = event.clientY;

    // 드래그 중일 때만 덱 영역 체크
    if (isDragging) {
        checkMouseInDeckPreview();
    }
});

// 마우스가 deckPreview 영역 내에 있는지 확인하는 함수
function checkMouseInDeckPreview() {
    const rect = deckPreview.getBoundingClientRect();
    isInsideDeck = mouseX >= rect.left && 
               mouseX <= rect.right && 
               mouseY >= rect.top && 
               mouseY <= rect.bottom;

    if (draggedFromDeck) { // 덱 안에서 드래그 시작
        if (isInsideDeck) {
            deckPreview.classList.remove('green-highlight', 'red-highlight');
        } else {
            deckPreview.classList.remove('green-highlight');
            deckPreview.classList.add('red-highlight');
        }
    } else { // 덱 밖에서 드래그 시작한 경우
        if (isInsideDeck) {
            deckPreview.classList.remove('red-highlight');
            deckPreview.classList.add('green-highlight');
        } else {
            deckPreview.classList.remove('green-highlight', 'red-highlight');
        }
    }
}

document.body.addEventListener('dragstart', function(event) {
    checkMouseInDeckPreview();

    // 드래그 가능한 카드 요소인지 확인
    const targetCard = event.target.closest('.deck-preview-card, .image-grid-element, .selected-card-image');

    if (targetCard) {
        draggedCardId = targetCard.getAttribute('card-id');
        isDragging = true;

        if (isInsideDeck) {
            draggedFromDeck = true;
        } else {
            draggedFromDeck = false;
        }
    } else {
        event.preventDefault(); // 기본 드래그 동작 방지
        draggedCardId = null;
    }
    console.log(mouseX, mouseY, isDragging, draggedFromDeck);
});

document.addEventListener('dragend', (event) => {
    if (draggedCardId) {
        const currentIds = getCardIdsFromUrl();
        let action = null;

        // 덱 밖에서 시작 -> 덱 안에서 드롭: 카드 추가
        if (!draggedFromDeck && isInsideDeck) {
            action = "add";
        }
        // 덱 안에서 시작 -> 덱 밖에서 드롭: 카드 제거
        else if (draggedFromDeck && !isInsideDeck) {
            action = "remove";
        }

        if (action) {
            $.ajax({
                url: baseUrl + '/' + lang + '/deck/check/',
                type: 'POST',
                data: JSON.stringify({
                    card_id: draggedCardId,
                    action: action,
                    current_card_ids: currentIds
                }),
                contentType: 'application/json',
                success: function(response) {
                    history.pushState(null, '', response.redirect_url);
                    refreshDeckPreview();
                },
                error: function(xhr, status, error) {
                    console.error("덱 변경 실패:", xhr);
                }
            });
        }
    }

    // 모든 드래그 작업이 끝난 후 상태 변수 및 하이라이트 초기화
    draggedCardId = null;
    draggedFromDeck = false;
    isInsideDeck = false;
    isDragging = false;
    // dragend 시점에 모든 하이라이트 제거를 확실히 함
    deckPreview.classList.remove('green-highlight', 'red-highlight');
});

function updateDeckPreview(response) {
    response = JSON.parse(response);
    const charCard = response["card_character"];
    const cardList = response["deck_card_list"];
    
    let deckHtml = '';
    const characterTrans = document.getElementById('deck-preview-data').dataset.characterTrans;
    const countStyle = response['num_cards'] > 30 ? 'style="color:red;"' : '';


    deckHtml += `
        <div class="deck-preview-card" onclick="selectCard(${charCard.id}, 0)" draggable="true" card-id="${charCard.id}">
            <div class="image-card" style="background-image: url(${charCard.d_url});"></div>
            <div class="image-frame" style="background-image: url(${charCard.d_frame});"></div>
            <div class="image-enhance" style="background-image: url(${charCard.d_frame_enh})${charCard.enhance == 0 ? ';display:none;' : ''}"></div>
            <div class="text-stat" id="card-enhance" ${charCard.enhance == 0 ? 'style="display:none;"' : ''}>${charCard.enhance}</div>
        </div>
        <div class="deck-preview-summary">
            <div class="deck-preview-summary-left">
                <img src="${staticUrl}card/Texture2D/UI_icon_card.webp" style="width:15%;">
                <p id="deck-preview-count" ${countStyle}>${response['num_cards']}</p>
                <p class="deck-preview-total">/ 30</p>
            </div>
            <p id="deck-preview-point">${response['deck_points']} PT</p>
        </div>
    `;

    cardList.forEach(card => {
        let cardName = (lang == 'ko') ? card.name : card.name_us;
        deckHtml += `
            <div class="deck-preview-card" onclick="selectCard(${card.id}, 0)" draggable="true" card-id="${card.id}">
                <div class="image-card" style="background-image: url(${card.d_url});"></div>
                <div class="image-frame" style="background-image: url(${card.d_frame});"></div>
                <div class="image-size" style="background-image: url(${card.d_frame_size})"></div>
                <div class="image-enhance" style="background-image: url(${card.frame_enh})${card.enhance == 0 ? ';display:none;' : ''}"></div>
                <div class="text-stat" id="card-enhance" ${card.enhance == 0 ? 'style="display:none;"' : ''}>${card.enhance}</div>
                <div class="text-stat" id="card-size" ${card.category == characterTrans ? 'style="display:none;"' : ''}>${card.size}</div>
                <div class="text-stat" id="card-count">x ${card.count}</div>
                <div class="text-stat" id="card-name">${cardName}</div>
            </div>
        `;
    });

    document.querySelector('.deck-preview').innerHTML = deckHtml;
}

function getCardIdsFromUrl() {
    const params = new URLSearchParams(window.location.search);
    const cards = params.get('card');
    return cards ? cards.split(',').map(id => parseInt(id)) : [];
}

function getDeckInfoFromUrl() {
    const params = new URLSearchParams(window.location.search);

    return {
        title: params.get('title') || 'None',
        summary: params.get('summary') || 'None',
        description: params.get('description') || 'None'
    };
}

function updateUrl(cardIds) {
    const newUrl = `${window.location.pathname}?card=${cardIds.join(',')}`;
    history.pushState(null, '', newUrl);
}

function refreshDeckPreview() {
    const cards = getCardIdsFromUrl().join(',')
    const deckInfo = getDeckInfoFromUrl();

    $.get('/deck/set/', {
        card: cards,
        title: deckInfo.title,
        summary: deckInfo.summary,
        description: deckInfo.description
    }, function(response) {
        updateDeckPreview(JSON.stringify(response));
        $('#deck-view').html(response.html);
    });
}