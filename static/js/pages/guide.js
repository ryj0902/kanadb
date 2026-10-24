import { startActions } from '../core/actions.js';
import { initCardDetail } from '../components/card-detail.js';
import { initTierVote } from '../components/tier-vote.js';
import { initCardTooltip } from '../components/tooltip.js';

initCardDetail();
initTierVote();
initCardTooltip();
startActions();
