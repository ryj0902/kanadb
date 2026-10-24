// data-action 이벤트 위임
//   <button data-action="select-card" data-card-id="1">  ->  onAction('select-card', (element, event) => ...)

const handlers = { click: new Map(), change: new Map() };

export function onAction(name, handler, eventType = 'click') {
    handlers[eventType].set(name, handler);
}

export function startActions(root = document) {
    Object.entries(handlers).forEach(([eventType, map]) => {
        root.addEventListener(eventType, (event) => {
            const element = event.target.closest('[data-action]');
            if (!element) return;
            const handler = map.get(element.dataset.action);
            if (handler) handler(element, event);
        });
    });
}
