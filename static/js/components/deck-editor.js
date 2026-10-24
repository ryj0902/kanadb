// 덱 페이지: 보기/편집 전환, 드래그로 카드 추가/제거, URL 기반 덱 미리보기

import { onAction } from '../core/actions.js';
import { getJson, postJson } from '../core/api.js';
import { qs } from '../core/dom.js';

// 덱 상태를 담는 쿼리 파라미터 (검색 폼 제출 시에도 유지)
const DECK_PARAMS = ['card', 'title', 'summary', 'description'];
const DRAGGABLE = '[draggable="true"][data-card-id]';

let root = null;
let dropZone = null;
let requestSeq = 0;

// --- 보기/편집 ---

function showTab(tab) {
    qs('#deck-edit', root).hidden = tab !== 'edit';
    qs('#deck-view', root).hidden = tab !== 'view';
    qs('#edit-button', root).classList.toggle('active', tab === 'edit');
    qs('#view-button', root).classList.toggle('active', tab === 'view');
}

// --- URL 상태 ---

function cardIdsFromUrl() {
    const cards = new URLSearchParams(window.location.search).get('card');
    return cards ? cards.split(',').map((id) => parseInt(id, 10)) : [];
}

// 검색 폼(GET) 제출 시에도 현재 덱이 유지되도록 hidden input을 URL과 맞춘다
function syncSearchForm() {
    const form = qs('#search-form', root);
    if (!form) return;
    const params = new URLSearchParams(window.location.search);
    DECK_PARAMS.forEach((name) => {
        let input = form.querySelector(`input[type="hidden"][name="${name}"]`);
        if (!params.has(name)) {
            if (input) input.remove();
            return;
        }
        if (!input) {
            input = document.createElement('input');
            input.type = 'hidden';
            input.name = name;
            form.prepend(input);
        }
        input.value = params.get(name);
    });
}

async function refreshDeck() {
    const params = new URLSearchParams(window.location.search);
    // 덱 정보가 비어 있으면 "None"으로 표시한다 (기존 동작)
    const query = new URLSearchParams({ card: params.get('card') || '' });
    ['title', 'summary', 'description'].forEach((name) => {
        query.set(name, params.get(name) || 'None');
    });
    const seq = ++requestSeq;
    const data = await getJson(`${root.dataset.setUrl}?${query}`);
    if (seq !== requestSeq) return;
    qs('.deck-preview', root).innerHTML = data.preview_html;
    qs('#deck-view', root).innerHTML = data.summary_html;
}

// 서버가 돌려준 새 덱으로 card만 바꾸고 다른 쿼리(덱 정보, 검색 조건)는 유지
function pushDeckUrl(redirectUrl) {
    const next = new URL(redirectUrl, window.location.origin);
    const params = new URLSearchParams(window.location.search);
    params.set('card', next.searchParams.get('card'));
    const query = params.toString().replace(/%2C/g, ',');
    window.history.pushState(null, '', `${next.pathname}?${query}`);
    syncSearchForm();
}

// --- 드래그 앤 드롭 ---

const drag = { cardId: null, fromDeck: false, insideDeck: false, active: false };
const mouse = { x: 0, y: 0 };

function updateDropHighlight() {
    const rect = dropZone.getBoundingClientRect();
    drag.insideDeck = mouse.x >= rect.left && mouse.x <= rect.right
        && mouse.y >= rect.top && mouse.y <= rect.bottom;

    // 덱 밖 -> 안: 추가(초록), 덱 안 -> 밖: 제거(빨강)
    dropZone.classList.toggle('green-highlight', !drag.fromDeck && drag.insideDeck);
    dropZone.classList.toggle('red-highlight', drag.fromDeck && !drag.insideDeck);
}

function onDragStart(event) {
    const card = event.target.closest(DRAGGABLE);
    if (!card) {
        event.preventDefault(); // 카드가 아닌 요소(이미지, 링크 등)는 끌지 않는다
        drag.cardId = null;
        return;
    }
    drag.cardId = card.dataset.cardId;
    drag.active = true;
    drag.fromDeck = dropZone.contains(card); // 덱 미리보기의 카드를 끌면 제거 동작
    updateDropHighlight();
}

function onDragOver(event) {
    event.preventDefault(); // 드롭 허용
    mouse.x = event.clientX;
    mouse.y = event.clientY;
    if (drag.active) updateDropHighlight();
}

async function onDragEnd() {
    let action = null;
    if (drag.cardId) {
        if (!drag.fromDeck && drag.insideDeck) action = 'add';
        else if (drag.fromDeck && !drag.insideDeck) action = 'remove';
    }
    const cardId = drag.cardId;

    Object.assign(drag, { cardId: null, fromDeck: false, insideDeck: false, active: false });
    dropZone.classList.remove('green-highlight', 'red-highlight');

    if (!action) return;
    try {
        const response = await postJson(root.dataset.checkUrl, {
            card_id: cardId,
            action,
            current_card_ids: cardIdsFromUrl(),
        });
        pushDeckUrl(response.redirect_url);
        refreshDeck();
    } catch (error) {
        console.error('덱 변경 실패:', error);
    }
}

export function initDeckEditor(element = qs('[data-deck]')) {
    if (!element) return;
    root = element;
    dropZone = qs('#deck-preview-content', root);

    onAction('deck-view', () => showTab('view'));
    onAction('deck-edit', () => showTab('edit'));

    document.addEventListener('mousemove', (event) => {
        mouse.x = event.clientX;
        mouse.y = event.clientY;
    });
    document.body.addEventListener('dragstart', onDragStart);
    document.addEventListener('dragover', onDragOver);
    document.addEventListener('dragend', onDragEnd);

    // 뒤로/앞으로 가기: URL의 덱으로 다시 그린다
    window.addEventListener('popstate', () => {
        syncSearchForm();
        refreshDeck();
    });

    refreshDeck();
}

