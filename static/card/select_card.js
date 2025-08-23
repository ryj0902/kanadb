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

    let product1_url = card.product1_url;
    let product1_str = (lang == 'ko') ? card.product1 : card.product1_us;
    let product2_url = card.product2_url;
    let product2_str = (lang == 'ko') ? card.product2 : card.product2_us;

    const button = document.getElementById('vert-horz-btn');
    const currentText = button.textContent.trim();
    const vert_horz = currentText === horizontalLayout ? 'vert': 'horz' 

    console.log(card);
    result = '' +
    '<div class="' + className + '-image'  + (card.producible ? '' : ' unproducible-card') + '"' + ' draggable="true" ' + 'card-id="' + card.id + '">' +
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
                '<div class="right-column">' +
                    '<p class="p-point">&nbsp;</p>' +
                    '<p class="p-point">' + card.point + ' PT</p>' +
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
        '</div>';

    result += '' +
    '<div class="' + className + '-product" style="display:none;">' + 
        '<table>';
    if (product1_url !== "-1") {
        result += '' +
            '<tr>' +
                '<td class="image-product" style="background-image: url(' + product1_url + ');"></td>' +
                '<td>' + product1_str + '</td>' +
            '</tr>';
    }
    if (product2_url !== "-1") {
        result += '' + 
            '<tr>' +
                '<td class="image-product" style="background-image: url(' + product2_url + ');"></td>' +
                '<td>' + product2_str + '</td>' +
            '</tr>';
    }
    result += '' +
        '</table>' +
    '</div>';

    result += '</div>'; // Close selected-card-texts

    return result
}

function selectCard(id, init_link){
    $.ajax({
        url: baseUrl + '/' + lang + '/card/select/' + id,
        type: 'GET',
        success: function(data) {
            const card = JSON.parse(data).selected_card;
            // console.log(data);

            document.getElementById('capture-btn').style.display = 'inline-block';
            document.getElementById('vert-horz-btn').style.display = 'inline-block';
            document.getElementById('hyperlink-btn').style.display = 'inline-block';
            document.getElementById('swap-text-btn').style.display = 'inline-block';

            // product
            document.getElementById('card-product-btn').style.display = 'inline-block';
            if (card.product1_url === "-1") {
                document.getElementById('card-product-btn').classList.add('grayscale')
            } else {
                document.getElementById('card-product-btn').classList.remove('grayscale')
            }

            enhance_card_prev = card.enh_prev;
            enhance_card_next = card.enh_next;
            enhance_card_orig = card.enh_orig;

            // enhance
            document.getElementById('card-enhance-img').style.display = 'inline-block';
            document.getElementById('card-enhance-down').style.display = 'inline-block';
            document.getElementById('card-enhance-up').style.display = 'inline-block';
            document.getElementById('card-enhance-down').style.opacity = (enhance_card_prev === -1) ? 0.5 : 1.0;
            document.getElementById('card-enhance-up').style.opacity = (enhance_card_next === -1) ? 0.5 : 1.0;

            // link
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

            // card description
            if (document.getElementsByClassName('selected-card-skill').length > 0) {
                swapTextTo('skill');
            }

            // re-rendering
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

function getLinkCard() {
    const selectedCard = document.querySelector('.selected-card-image');
    const cardId = selectedCard.getAttribute('card-id')
    const button = document.getElementById('hyperlink-btn');

    const baseUrl = window.location.origin;
    const link = `${baseUrl}/card/#selectCard/${cardId}/0`;
    
    if (navigator.clipboard && navigator.clipboard.writeText) {
        navigator.clipboard.writeText(link)
            .then(() => {
                button.textContent = "✅";
            })
            .catch(err => {
                console.error("클립보드 복사 실패: ", err);
                alert("클립보드 복사에 실패했습니다.");
            });
    } else {
        // http 환경
        const textarea = document.createElement("textarea");
        textarea.value = link;
        document.body.appendChild(textarea);
        textarea.select();
        try {
            document.execCommand("copy");
            button.textContent = "✅";
        } catch (err) {
            console.error("Fallback 복사 실패: ", err);
            alert("클립보드 복사에 실패했습니다.");
        }
        document.body.removeChild(textarea);
    }
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
    selectCard(enhance_card_orig, 1);
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

function toggleProducts() {
    const element = document.getElementsByClassName('selected-card-product')[0];
    element.style.display = (element.style.display === 'none' || element.style.display === '') 
            ? 'inline-block' 
            : 'none';
}

function attachTooltipHandler() {
    let tooltipTimer = null;
    let activeTooltip = null;
    let currentCard = null;
    let currentMouseX = 0;
    let currentMouseY = 0;

    document.body.addEventListener('mousemove', (e) => {
        currentMouseX = e.pageX;
        currentMouseY = e.pageY;

        // If a tooltip is already active, update its position immediately
        if (activeTooltip) {
            updateTooltipPosition(currentMouseX, currentMouseY);
        }
    });

    // Function to hide the active tooltip
    const hideTooltip = () => {
        if (activeTooltip) {
            activeTooltip.remove();
            activeTooltip = null;
        }
        if (tooltipTimer) {
            clearTimeout(tooltipTimer);
            tooltipTimer = null;
        }
        // Remove event listeners that track mouse movement for the tooltip
        document.removeEventListener('mousemove', updateTooltipPosition);
        // Clean up the mouseout listener from the *previously hovered card*
        if (currentCard) {
            currentCard.removeEventListener('mouseleave', handleCardMouseLeave);
            currentCard = null;
        }
    };

    // Function to update tooltip position
    const updateTooltipPosition = (x, y) => {
        if (activeTooltip) {
            activeTooltip.style.left = `${x + 15}px`;
            activeTooltip.style.top = `${y + 15}px`;
        }
    };

    // Handle mouse leaving the card
    const handleCardMouseLeave = () => {
        hideTooltip();
    };

    // Main mouseover handler on the document body
    document.body.addEventListener('mouseover', (e) => {
        const card = e.target.closest('.image-card');

        // If no card is hovered, or if we're already hovering the same card, or if a tooltip is already active, hide any existing tooltip and return.
        if (!card) {
            hideTooltip();
            return;
        }

        // If the mouse is still over the same card, do nothing
        if (card === currentCard) {
            return;
        }

        // If hovering a new card, hide any existing tooltip first
        hideTooltip();

        currentCard = card; // Set the current hovered card

        const cardContainer = card.closest('[card-id]');
        if (!cardContainer) return;

        const cardId = cardContainer.getAttribute('card-id');
        if (!cardId) return;

        const delay = 350;
        tooltipTimer = setTimeout(() => {
            // If another tooltip has appeared or the card is no longer hovered,
            // or the card has been removed from the DOM, prevent showing.
            if (activeTooltip || !document.body.contains(card)) {
                tooltipTimer = null;
                return;
            }

            const tooltip = Object.assign(document.createElement('div'), {
                className: 'custom-tooltip',
                textContent: `CARD_${cardId}`
            });
            document.body.appendChild(tooltip);
            activeTooltip = tooltip;

            updateTooltipPosition(currentMouseX, currentMouseY);

            // Attach listeners for dynamic positioning and hiding
            document.addEventListener('mousemove', updateTooltipPosition);
            card.addEventListener('mouseleave', handleCardMouseLeave);

            tooltipTimer = null; // Clear the timer after tooltip is shown
        }, delay);

        // This listener ensures that if the mouse leaves the card *before* the delay,
        // the timer is cleared and no tooltip appears.
        card.addEventListener('mouseleave', () => {
            if (tooltipTimer) {
                clearTimeout(tooltipTimer);
                tooltipTimer = null;
            }
            // If the mouse leaves and no tooltip has been shown yet,
            // also clear the `currentCard` reference
            if (!activeTooltip) {
                currentCard = null;
            }
        }, { once: true }); // Use { once: true } to automatically remove this listener after it fires
    });

    // Handle cases where the mouse might leave the entire document or a tooltip is active
    // but not over a specific card. This is a fallback to ensure cleanup.
    document.body.addEventListener('mouseout', (e) => {
        // If the mouse leaves an image card, and it's not entering another image card, hide the tooltip.
        // This helps when dragging a card out of the view or onto an area without cards.
        if (e.target.closest('.image-card') && !e.relatedTarget?.closest('.image-card')) {
            hideTooltip();
        }
    });
}