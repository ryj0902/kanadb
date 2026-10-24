// 가이드 티어 리스트 투표 (같은 티어를 다시 누르면 취소)

import { onAction } from '../core/actions.js';
import { postJson } from '../core/api.js';
import { qs } from '../core/dom.js';

export function initTierVote(root = qs('[data-guide-body]')) {
    if (!root) return;

    onAction('vote', async (image) => {
        const { cardId, category, mode, tier } = image.dataset;
        try {
            const response = await postJson(root.dataset.voteUrl, {
                card_id: Number(cardId),
                category,
                mode: Number(mode),
                tier: Number(tier),
            });
            root.innerHTML = response.html_content;
        } catch (error) {
            console.error('투표 실패:', error);
        }
    });
}
