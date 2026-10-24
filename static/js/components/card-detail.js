// 카드 상세 패널: 카드 선택, 강화/링크 카드 이동, 텍스트 전환, 상품, 가로/세로, 캡처, 링크 복사

import { onAction } from '../core/actions.js';
import { getJson, urlWithId } from '../core/api.js';
import { hide, qs, qsa, show } from '../core/dom.js';
import { loadScript } from '../core/script-loader.js';

const NONE = -1;
const COPY_RESTORE_MS = 2000;
// 텍스트 패널 순환: 스킬 -> 스토리 -> 대사 -> 스킬
const NEXT_TEXT = { skill: 'story', story: 'dial', dial: 'skill' };

let panel = null;
let requestSeq = 0;
let horizontal = false;
const state = {
    cardId: null,
    originId: null, // 링크 이동을 시작한 카드
    linkIds: [],
    linkIndex: 0,
    enhPrev: NONE,
    enhNext: NONE,
    enhOrig: NONE,
};

const control = (action) => qs(`[data-action="${action}"]`, panel);

export async function selectCard(cardId, resetLink = true) {
    const seq = ++requestSeq;
    const { html, state: card } = await getJson(urlWithId(panel.dataset.selectUrl, cardId));
    if (seq !== requestSeq) return; // 늦게 도착한 이전 요청의 응답은 버린다

    state.cardId = card.id;
    ['capture-card', 'toggle-layout', 'copy-link', 'swap-text', 'toggle-products',
        'enhance-reset', 'enhance-prev', 'enhance-next'].forEach((id) => show(control(id)));
    control('toggle-products').classList.toggle('is-unavailable', !card.has_product);

    state.enhPrev = card.enh_prev;
    state.enhNext = card.enh_next;
    state.enhOrig = card.enh_orig;
    control('enhance-prev').style.opacity = card.enh_prev === NONE ? 0.5 : 1.0;
    control('enhance-next').style.opacity = card.enh_next === NONE ? 0.5 : 1.0;

    if (resetLink) {
        state.originId = card.id;
        state.linkIds = card.link_ids;
        state.linkIndex = 0;
        show(control('link-open'));
        control('link-open').classList.toggle('is-unavailable', card.link_ids.length === 0);
        ['link-prev', 'link-reset', 'link-next'].forEach((id) => hide(control(id)));
    }

    resetTextButton();
    qs('[data-card-detail-body]', panel).innerHTML = html;
}

// --- 링크 카드 ---

function showLinkCard(offset) {
    const { linkIds } = state;
    const index = state.linkIndex + offset;
    if (linkIds.length === 0 || index < 0 || index >= linkIds.length) return;

    state.linkIndex = index;
    control('link-prev').style.opacity = index === 0 ? 0.5 : 1.0;
    control('link-next').style.opacity = index + 1 < linkIds.length ? 1.0 : 0.5;
    selectCard(linkIds[index], false);

    hide(control('link-open'));
    ['link-prev', 'link-reset', 'link-next'].forEach((id) => show(control(id)));
}

function resetLinkCard() {
    selectCard(state.originId, true);
}

// --- 강화 단계 ---

function showEnhanceCard(offset) {
    const target = offset < 0 ? state.enhPrev : state.enhNext;
    if (target !== NONE) selectCard(target, false);
}

// --- 텍스트(스킬/스토리/대사) ---

function resetTextButton() {
    const button = control('swap-text');
    button.src = button.dataset.iconStory;
    button.dataset.next = 'story';
}

function swapText(button) {
    const mode = button.dataset.next || 'story';
    qsa('[data-text-panel]', panel).forEach((element) => {
        element.hidden = element.dataset.textPanel !== mode;
    });
    const next = NEXT_TEXT[mode];
    button.src = button.dataset[`icon${next[0].toUpperCase()}${next.slice(1)}`];
    button.dataset.next = next;
}

// --- 보기 ---

function toggleProducts() {
    const products = qs('[data-card-products]', panel);
    if (products) products.hidden = !products.hidden;
}

function toggleLayout(button) {
    horizontal = !horizontal;
    panel.classList.toggle('is-horizontal', horizontal);
    panel.closest('[data-aside]')?.classList.toggle('is-horizontal', horizontal);
    button.textContent = horizontal ? panel.dataset.verticalLabel : panel.dataset.horizontalLabel;
}

async function captureCard() {
    await loadScript(panel.dataset.html2canvasSrc);
    const canvas = await window.html2canvas(qs('[data-card-detail-body]', panel));
    const link = document.createElement('a');
    link.href = canvas.toDataURL('image/png');
    link.download = `${qs('[data-card-name]', panel).textContent}.png`;
    link.click();
}

// --- 공유 링크 ---

function cardLink(cardId) {
    // 언어 prefix 없이 공유하면 받는 사람의 언어로 열린다
    return `${window.location.origin}/card/#selectCard/${cardId}/0`;
}

async function writeClipboard(text) {
    if (navigator.clipboard && navigator.clipboard.writeText) {
        await navigator.clipboard.writeText(text);
        return;
    }
    // http 환경
    const textarea = document.createElement('textarea');
    textarea.value = text;
    document.body.appendChild(textarea);
    textarea.select();
    try {
        if (!document.execCommand('copy')) throw new Error('copy command failed');
    } finally {
        textarea.remove();
    }
}

async function copyLink(button) {
    if (!button.dataset.label) button.dataset.label = button.textContent;
    try {
        await writeClipboard(cardLink(state.cardId));
        button.textContent = '✅';
        clearTimeout(Number(button.dataset.restoreTimer));
        button.dataset.restoreTimer = setTimeout(() => {
            button.textContent = button.dataset.label;
        }, COPY_RESTORE_MS);
    } catch (error) {
        console.error(error);
        alert(panel.dataset.copyFailed);
    }
}

export function initCardDetail(root = qs('[data-card-detail]')) {
    if (!root) return;
    panel = root;

    onAction('select-card', (element, event) => {
        event.preventDefault();
        selectCard(element.dataset.cardId, true);
    });
    onAction('capture-card', captureCard);
    onAction('toggle-layout', toggleLayout);
    onAction('copy-link', copyLink);
    onAction('toggle-products', toggleProducts);
    onAction('swap-text', swapText);
    onAction('enhance-prev', () => showEnhanceCard(-1));
    onAction('enhance-next', () => showEnhanceCard(1));
    onAction('enhance-reset', () => selectCard(state.enhOrig, false));
    onAction('link-open', () => showLinkCard(0));
    onAction('link-prev', () => showLinkCard(-1));
    onAction('link-next', () => showLinkCard(1));
    onAction('link-reset', resetLinkCard);
}
