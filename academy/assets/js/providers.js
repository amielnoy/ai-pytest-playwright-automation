import { $ } from './dom.js';
import { S } from './i18n.js';
export const PROVIDERS = {
    gemini: {
        label: S.keyLabelGemini,
        placeholder: 'AIza...',
        models: ['gemini-2.5-flash', 'gemini-2.5-flash-lite', 'gemini-2.5-pro'],
        build(key, model, system, messages, maxTokens) {
            const generationConfig = { maxOutputTokens: maxTokens };
            if (model.includes('flash'))
                generationConfig.thinkingConfig = { thinkingBudget: 0 };
            return {
                url: 'https://generativelanguage.googleapis.com/v1beta/models/' + model + ':generateContent',
                headers: { 'content-type': 'application/json', 'x-goog-api-key': key },
                body: {
                    system_instruction: { parts: [{ text: system }] },
                    contents: messages.map(m => ({
                        role: m.role === 'assistant' ? 'model' : 'user',
                        parts: [{ text: m.content }]
                    })),
                    generationConfig
                }
            };
        },
        parse: d => (d.candidates?.[0]?.content?.parts || []).map((p) => p.text || '').join('\n'),
        keyHint: (key, status) => [400, 401, 403].includes(status) && !key.startsWith('AIza') ? S.errGeminiKeyHint : ''
    },
    anthropic: {
        label: S.keyLabelAnthropic,
        placeholder: 'sk-ant-...',
        models: ['claude-sonnet-5', 'claude-haiku-4-5-20251001'],
        validateKey(key) { if (!key.startsWith('sk-ant-'))
            throw new Error(S.errKeyNotAnthropic); },
        build(key, model, system, messages, maxTokens) {
            return {
                url: 'https://api.anthropic.com/v1/messages',
                headers: {
                    'content-type': 'application/json',
                    'x-api-key': key,
                    'anthropic-version': '2023-06-01',
                    'anthropic-dangerous-direct-browser-access': 'true'
                },
                body: { model, max_tokens: maxTokens, system, messages }
            };
        },
        parse: d => d.content.filter((b) => b.type === 'text').map((b) => b.text).join('\n')
    },
    openai: {
        label: S.keyLabelOpenai,
        placeholder: 'sk-...',
        models: ['gpt-5-mini', 'gpt-5.4-mini', 'gpt-5.4'],
        validateKey(key) { if (key.startsWith('sk-ant-'))
            throw new Error(S.errKeyNotOpenai); },
        build(key, model, system, messages, maxTokens) {
            return {
                url: 'https://api.openai.com/v1/chat/completions',
                headers: { 'content-type': 'application/json', 'Authorization': 'Bearer ' + key },
                body: { model, max_completion_tokens: maxTokens, messages: [{ role: 'system', content: system }, ...messages] }
            };
        },
        parse: d => d.choices?.[0]?.message?.content || ''
    }
};
function currentProvider() { return $('providerSel').value; }
/* localStorage slot holding the user's own key for the active provider. */
function providerKeyStore() { return 'ata_key_' + currentProvider(); }
/* keys loaded from .env (works when the page is served over http, e.g. python3 -m http.server) */
const envKeys = {};
const ENV_VAR_BY_PROVIDER = { gemini: 'GEMINI_API_KEY', anthropic: 'ANTHROPIC_API_KEY', openai: 'OPENAI_API_KEY' };
let ownKeyTouched = false; // becomes true once the user ticks the checkbox themselves
async function loadEnvFile() {
    try {
        const res = await fetch('../.env', { cache: 'no-store' });
        if (!res.ok)
            return;
        for (const line of (await res.text()).split('\n')) {
            const m = line.match(/^\s*([A-Z0-9_]+)\s*=\s*(.+?)\s*$/);
            if (m && !m[1].startsWith('#'))
                envKeys[m[1]] = m[2].replace(/^["']|["']$/g, '');
        }
        if (!ownKeyTouched)
            applyKeyMode(); // re-evaluate defaults; UI-saved keys still win
    }
    catch { /* file:// or no .env — manual key entry still works */ }
}
function envKeyFor(provider) { return envKeys[ENV_VAR_BY_PROVIDER[provider]] || ''; }
/* Gate the key input behind the checkbox: the .env key is the locked-in default,
   and a custom key can only be entered after ticking "Use my own API key". */
function applyKeyMode() {
    const p = PROVIDERS[currentProvider()];
    const envKey = envKeyFor(currentProvider());
    // default state (until the user touches the box): UI-saved key wins first,
    // then the .env key; own-key mode when there's no .env key at all.
    if (!ownKeyTouched)
        $('useOwnKey').checked = !!localStorage.getItem(providerKeyStore()) || !envKey;
    const own = $('useOwnKey').checked;
    $('useOwnKey').disabled = !envKey; // can't turn off what doesn't exist
    $('ownKeyRow').style.opacity = envKey ? '1' : '.5';
    $('apiKey').disabled = !own;
    $('apiKey').placeholder = own ? p.placeholder : S.placeholderEnvKey;
    if (own) {
        $('apiKey').value = localStorage.getItem(providerKeyStore()) || '';
        $('apiKeyLabel').textContent = p.label;
    }
    else {
        $('apiKey').value = envKey;
        $('apiKeyLabel').textContent = p.label.replace(S.labelSuffixLocal, S.labelSuffixEnv);
    }
}
export function onProviderChange() {
    const p = PROVIDERS[currentProvider()];
    $('modelSel').innerHTML = p.models.map(m => `<option value="${m}">${m}</option>`).join('');
    ownKeyTouched = false; // each provider re-evaluates its own default
    applyKeyMode();
}
export async function callClaude(system, messages, maxTokens = 2500) {
    const key = $('apiKey').value.trim();
    if (!key)
        throw new Error(S.errNoKey);
    const provider = PROVIDERS[currentProvider()];
    provider.validateKey?.(key);
    const { url, headers, body } = provider.build(key, $('modelSel').value, system, messages, maxTokens);
    let res;
    try {
        res = await fetch(url, { method: 'POST', headers, body: JSON.stringify(body) });
    }
    catch {
        throw new Error(S.errBlockedPrefix + new URL(url).host + S.errBlockedMid +
            S.errBlockedCauses +
            S.errBlockedTry +
            S.errBlockedOpenUrl);
    }
    if (!res.ok) {
        const errBody = await res.text();
        const hint = provider.keyHint ? provider.keyHint(key, res.status) : '';
        throw new Error(S.errApiPrefix + res.status + '): ' + errBody.slice(0, 300) + hint);
    }
    return provider.parse(await res.json());
}
export function resetSettings() {
    Object.keys(localStorage).filter(k => k.startsWith('ata_')).forEach(k => localStorage.removeItem(k));
    location.reload();
}
export async function testConnection() {
    const el = $('connStatus');
    el.style.color = 'var(--muted)';
    el.textContent = S.statusTesting;
    try {
        const reply = await callClaude(S.pingSystem, [{ role: 'user', content: S.pingUser }], 20);
        el.style.color = 'var(--green)';
        el.textContent = S.statusOkPrefix + $('modelSel').value + '): ' + reply.slice(0, 40);
    }
    catch (e) {
        el.style.color = 'var(--red)';
        el.textContent = '❌ ' + e.message;
    }
}
export function extractJSON(text) {
    const fenced = text.match(/```(?:json)?\s*([\s\S]*?)```/);
    const raw = fenced ? fenced[1] : text;
    const start = raw.indexOf('{'), end = raw.lastIndexOf('}');
    if (start === -1 || end === -1)
        throw new Error(S.errNoJson);
    return JSON.parse(raw.slice(start, end + 1));
}
/* Wire the provider select + key-gating controls and load the .env defaults. */
export function initProviders() {
    $('useOwnKey').addEventListener('change', () => { ownKeyTouched = true; applyKeyMode(); });
    loadEnvFile();
    $('providerSel').value = localStorage.getItem('ata_provider') || 'gemini';
    onProviderChange();
    $('providerSel').addEventListener('change', () => localStorage.setItem('ata_provider', currentProvider()));
    $('apiKey').addEventListener('change', () => localStorage.setItem(providerKeyStore(), $('apiKey').value.trim()));
}
