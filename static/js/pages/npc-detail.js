import { startActions } from '../core/actions.js';
import { initCardDetail } from '../components/card-detail.js';
import { initFloorNav } from '../components/floor-nav.js';
import { initCardTooltip } from '../components/tooltip.js';

initCardDetail();
initFloorNav();
initCardTooltip();
startActions();
