// 필요할 때만 일반 스크립트(UMD 라이브러리)를 불러온다

const loaded = new Map();

export function loadScript(src) {
    if (!loaded.has(src)) {
        loaded.set(src, new Promise((resolve, reject) => {
            const script = document.createElement('script');
            script.src = src;
            script.onload = resolve;
            script.onerror = () => reject(new Error(`failed to load ${src}`));
            document.head.appendChild(script);
        }));
    }
    return loaded.get(src);
}
