// 덱 페이지: 보기/편집 전환, 드래그로 카드 추가/제거, 덱 정보 수정, URL 기반 덱 미리보기

import { onAction } from '../core/actions.js';
import { getJson, postJson } from '../core/api.js';
import { qs, qsa } from '../core/dom.js';

// 덱 정보(제목/요약/설명) 쿼리 파라미터. 비어 있으면 "None"으로 표시한다 (기존 동작)
const META_PARAMS = ['title', 'summary', 'description'];
const EMPTY_META = 'None';
// 덱 상태를 담는 쿼리 파라미터 (검색 폼 제출 시에도 유지)
const DECK_PARAMS = ['card', ...META_PARAMS];
const DRAGGABLE = '[draggable="true"][data-card-id]';

let root = null;
let dropZone = null;
let requestSeq = 0;

// --- 보기/편집 ---

function showTab(tab) {
    qsa('[data-deck-panel]', root).forEach((panel) => {
        panel.hidden = panel.dataset.deckPanel !== tab;
    });
    qsa('[data-deck-tab]', root).forEach((button) => {
        button.classList.toggle('is-active', button.dataset.deckTab === tab);
    });
}

// --- URL 상태 ---

function cardIdsFromUrl() {
    const cards = new URLSearchParams(window.location.search).get('card');
    return cards ? cards.split(',').map((id) => parseInt(id, 10)) : [];
}

// 검색 폼(GET) 제출 시에도 현재 덱이 유지되도록 hidden input을 URL과 맞춘다
function syncSearchForm() {
    const form = qs('[data-search-form]', root);
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

// 언어 전환 링크는 서버가 처음 연 URL로 만들었으므로 바뀐 쿼리를 따라가게 한다
function syncLanguageLinks() {
    qsa('[data-language-link]').forEach((link) => {
        const url = new URL(link.href);
        url.search = window.location.search;
        link.href = url;
    });
}

function pushQuery(params, pathname = window.location.pathname) {
    const query = params.toString().replace(/%2C/g, ',');
    window.history.pushState(null, '', `${pathname}?${query}`);
    syncSearchForm();
    syncLanguageLinks();
}

async function refreshDeck() {
    const params = new URLSearchParams(window.location.search);
    const query = new URLSearchParams({ card: params.get('card') || '' });
    META_PARAMS.forEach((name) => {
        query.set(name, params.get(name) || EMPTY_META);
    });
    const seq = ++requestSeq;
    const data = await getJson(`${root.dataset.setUrl}?${query}`);
    if (seq !== requestSeq) return;
    qs('[data-deck-preview]', root).innerHTML = data.preview_html;
    qs('[data-deck-panel="view"]', root).innerHTML = data.summary_html;
}

// 서버가 돌려준 새 덱으로 card만 바꾸고 다른 쿼리(덱 정보, 검색 조건)는 유지
function pushDeckUrl(redirectUrl) {
    const next = new URL(redirectUrl, window.location.origin);
    const params = new URLSearchParams(window.location.search);
    params.set('card', next.searchParams.get('card'));
    pushQuery(params, next.pathname);
}

// --- 덱 정보(제목/요약/설명) 보기/수정 ---

function setMetaMode(field, mode) {
    qsa('[data-deck-meta-mode]', field).forEach((element) => {
        element.hidden = element.dataset.deckMetaMode !== mode;
    });
}

function editMeta(field) {
    const input = qs('[data-deck-meta-input]', field);
    input.value = new URLSearchParams(window.location.search).get(field.dataset.deckMeta) || '';
    setMetaMode(field, 'edit');
    input.focus();
    input.setSelectionRange(input.value.length, input.value.length);
}

function closeMeta(field) {
    setMetaMode(field, 'view');
    qs('[data-action="deck-meta-edit"]', field).focus();
}

// 적용: URL의 덱 정보를 바꾸고(뒤로 가기로 되돌릴 수 있음) 글자만 바로 고친다
function saveMeta(field) {
    const name = field.dataset.deckMeta;
    const value = qs('[data-deck-meta-input]', field).value.trim();
    const params = new URLSearchParams(window.location.search);
    if (value !== (params.get(name) || '')) {
        if (value) params.set(name, value);
        else params.delete(name);
        pushQuery(params);
    }
    qs('[data-deck-meta-text]', field).textContent = value || EMPTY_META;
    closeMeta(field);
}

function onMetaKeydown(event) {
    const input = event.target.closest('[data-deck-meta-input]');
    if (!input || event.isComposing) return; // 한글 조합 중의 Enter는 글자 확정
    const field = input.closest('[data-deck-meta]');
    if (event.key === 'Escape') {
        closeMeta(field);
    } else if (event.key === 'Enter' && !event.shiftKey) {
        // Enter로 적용, 설명(여러 줄)의 줄바꿈은 Shift+Enter
        event.preventDefault();
        saveMeta(field);
    }
}

// --- 드래그 앤 드롭 ---

const drag = { cardId: null, fromDeck: false, insideDeck: false, active: false };
const mouse = { x: 0, y: 0 };

function updateDropHighlight() {
    const rect = dropZone.getBoundingClientRect();
    drag.insideDeck = mouse.x >= rect.left && mouse.x <= rect.right
        && mouse.y >= rect.top && mouse.y <= rect.bottom;

    // 덱 밖 -> 안: 추가(초록), 덱 안 -> 밖: 제거(빨강)
    dropZone.classList.toggle('is-drop-add', !drag.fromDeck && drag.insideDeck);
    dropZone.classList.toggle('is-drop-remove', drag.fromDeck && !drag.insideDeck);
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
    dropZone.classList.remove('is-drop-add', 'is-drop-remove');

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
    dropZone = qs('[data-deck-drop]', root);

    onAction('deck-view', () => showTab('view'));
    onAction('deck-edit', () => showTab('edit'));

    const metaField = (button) => button.closest('[data-deck-meta]');
    onAction('deck-meta-edit', (button) => editMeta(metaField(button)));
    onAction('deck-meta-save', (button) => saveMeta(metaField(button)));
    onAction('deck-meta-cancel', (button) => closeMeta(metaField(button)));
    root.addEventListener('keydown', onMetaKeydown);

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
        syncLanguageLinks();
        refreshDeck();
    });

    refreshDeck();
}

