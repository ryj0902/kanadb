// 카드 그림에 마우스를 잠시 올리면 카드 id(CARD_<id>) 툴팁 표시

const DELAY_MS = 350;
const OFFSET_PX = 15;

export function initCardTooltip() {
    let tooltip = null;
    let timer = null;
    let currentArt = null;
    let mouseX = 0;
    let mouseY = 0;

    const place = () => {
        if (!tooltip) return;
        tooltip.style.left = `${mouseX + OFFSET_PX}px`;
        tooltip.style.top = `${mouseY + OFFSET_PX}px`;
    };

    const hideTooltip = () => {
        clearTimeout(timer);
        timer = null;
        if (tooltip) {
            tooltip.remove();
            tooltip = null;
        }
        currentArt = null;
    };

    document.body.addEventListener('mousemove', (event) => {
        mouseX = event.pageX;
        mouseY = event.pageY;
        place();
    });

    document.body.addEventListener('mouseover', (event) => {
        const art = event.target.closest('[data-card-art]');
        if (!art) {
            hideTooltip();
            return;
        }
        if (art === currentArt) return;

        hideTooltip();
        const owner = art.closest('[data-card-id]');
        if (!owner) return;
        currentArt = art;

        timer = setTimeout(() => {
            if (!document.body.contains(art)) return;
            tooltip = document.createElement('div');
            tooltip.className = 'card-tooltip';
            tooltip.textContent = `CARD_${owner.dataset.cardId}`;
            document.body.appendChild(tooltip);
            place();
        }, DELAY_MS);
    });

    document.body.addEventListener('mouseout', (event) => {
        if (event.target.closest('[data-card-art]') && !event.relatedTarget?.closest('[data-card-art]')) {
            hideTooltip();
        }
    });
}
