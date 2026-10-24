import { startActions } from '../core/actions.js';
import { initCardDetail, selectCard } from '../components/card-detail.js';
import { initCardSearch } from '../components/card-search.js';
import { initCardTooltip } from '../components/tooltip.js';

initCardDetail();
initCardSearch();
initCardTooltip();
startActions();

// 공유 링크: #selectCard/<card_id>/<init_link> 만 허용
const match = window.location.hash.match(/^#selectCard\/(\d+)(?:\/(\d+))?$/);
if (match) {
    selectCard(match[1], Number(match[2]) === 0);
}
