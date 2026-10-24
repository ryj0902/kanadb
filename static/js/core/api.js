// fetch 래퍼: JSON/HTML 요청, CSRF 토큰, 오류 처리

function csrfToken() {
    const meta = document.querySelector('meta[name="csrf-token"]');
    return meta ? meta.content : '';
}

async function request(url, options = {}) {
    const response = await fetch(url, {
        credentials: 'same-origin',
        ...options,
        headers: { 'X-Requested-With': 'fetch', ...(options.headers || {}) },
    });
    if (!response.ok) {
        throw new Error(`${options.method || 'GET'} ${url} -> ${response.status}`);
    }
    return response;
}

export async function getJson(url, { signal } = {}) {
    const response = await request(url, { signal });
    return response.json();
}

export async function getHtml(url, { headers, signal } = {}) {
    const response = await request(url, { headers, signal });
    return response.text();
}

export async function postJson(url, data) {
    const response = await request(url, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', 'X-CSRFToken': csrfToken() },
        body: JSON.stringify(data),
    });
    return response.json();
}

// URL 템플릿의 마지막 경로 조각 0을 id로 바꾼다 ("/ko/card/select/0" -> "/ko/card/select/123")
export function urlWithId(template, id) {
    return template.replace(/0$/, String(id));
}
