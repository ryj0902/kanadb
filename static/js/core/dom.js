// DOM 도우미

export const qs = (selector, root = document) => root.querySelector(selector);

export const qsa = (selector, root = document) => Array.from(root.querySelectorAll(selector));

export function show(element, visible = true) {
    element.hidden = !visible;
}

export function hide(element) {
    element.hidden = true;
}

// HTML 문자열 -> DocumentFragment
export function parseHtml(html) {
    const template = document.createElement('template');
    template.innerHTML = html;
    return template.content;
}
