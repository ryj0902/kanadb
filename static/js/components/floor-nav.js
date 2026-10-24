// NPC 상세: 난이도/층 선택 시 해당 NPC로 이동

import { onAction } from '../core/actions.js';

export function initFloorNav() {
    onAction('navigate', (select) => {
        if (select.value) window.location.href = select.value;
    }, 'change');
}
