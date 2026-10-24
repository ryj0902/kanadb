// 카드 검색: 필터 탭, 전체 선택, 검색어 동기화, 결과 페이지 이동

import { onAction } from '../core/actions.js';
import { getHtml } from '../core/api.js';
import { qs, qsa } from '../core/dom.js';

let root = null;
let page = 1;
let pageTotal = 1;
let requestSeq = 0;

function openTab(tab) {
    qsa('[data-filter-tab]', root).forEach((panel) => {
        panel.hidden = panel.dataset.filterTab !== tab;
    });
    qsa('[data-action="open-tab"]', root).forEach((button) => {
        button.classList.toggle('is-active', button.dataset.tab === tab);
    });
    // 엔터로 제출해도 현재 탭으로 돌아오도록 모든 검색 버튼 값을 맞춘다
    qsa('button[type="submit"][name="tab"]', root).forEach((button) => {
        button.value = tab;
    });
}

function toggleAll(checkbox) {
    qsa(`input[name="${checkbox.dataset.target}"]`, root).forEach((input) => {
        input.checked = checkbox.checked;
    });
}

// 탭마다 있는 검색어 입력칸(같은 name)을 같은 값으로 유지
function syncSearchText(event) {
    const { name, value } = event.target;
    if (name !== 'search_text' && name !== 'search_type') return;
    qsa(`[name="${name}"]`, root).forEach((input) => {
        if (input !== event.target) input.value = value;
    });
}

async function goToPage(target) {
    page = Math.min(Math.max(target, 1), pageTotal);
    qs('[data-page-label]', root).textContent = `${page} / ${pageTotal}`;

    // 현재 URL에 적용된 검색 조건 그대로 다음 페이지
    const params = new URLSearchParams(window.location.search);
    params.set('page', page);
    const seq = ++requestSeq;
    const html = await getHtml(`${root.dataset.gridUrl}?${params}`, {
        headers: { 'X-Partial': 'card-grid' },
    });
    if (seq !== requestSeq) return;
    qs('[data-card-grid]', root).innerHTML = html;
}

export function initCardSearch(element = qs('[data-card-search]')) {
    if (!element) return;
    root = element;
    page = Number(root.dataset.page);
    pageTotal = Number(root.dataset.pageTotal);

    onAction('open-tab', (button) => openTab(button.dataset.tab));
    onAction('toggle-all', toggleAll);
    onAction('page-prev', () => goToPage(page - 1));
    onAction('page-next', () => goToPage(page + 1));
    root.addEventListener('input', syncSearchText);
    root.addEventListener('change', syncSearchText);
}
