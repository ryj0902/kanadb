import { startActions } from '../core/actions.js';
import { initCardDetail } from '../components/card-detail.js';
import { initCardSearch } from '../components/card-search.js';
import { initDeckEditor } from '../components/deck-editor.js';
import { initCardTooltip } from '../components/tooltip.js';

initCardDetail();
initCardSearch();
initDeckEditor();
initCardTooltip();
startActions();
