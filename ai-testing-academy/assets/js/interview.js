import { $ } from './dom.js';
import { L, S } from './i18n.js';
import { callClaude } from './providers.js';
import { speak, stopSpeaking, toggleRecognition, ttsSupported, sttSupported } from './voice.js';
const INTERVIEW_SYSTEM = L.prompts.interview;
let chat = [];
let interviewOn = false;
let voiceOn = !!localStorage.getItem('ata_voice');
function addMsg(cls, text) {
    const div = document.createElement('div');
    div.className = 'msg ' + cls;
    div.textContent = text;
    const box = $('chatBox');
    box.appendChild(div);
    box.scrollTop = box.scrollHeight;
    return div;
}
/* Reflect the mic button's listening state. */
function setMicState(listening) {
    const mic = document.getElementById('micBtn');
    if (!mic)
        return;
    mic.classList.toggle('listening', listening);
    mic.textContent = listening ? '⏹️' : '🎙️';
    mic.title = listening ? S.micListening : S.micTitle;
    mic.setAttribute('aria-label', listening ? S.micListening : S.micTitle);
}
/* Start/stop listening; a final transcript is sent as the answer. */
function beginListening() {
    if (!interviewOn)
        return;
    toggleRecognition(text => { $('chatInput').value = text; if (text.trim())
        sendAnswer(); }, setMicState);
}
async function agentTurn(autoListen = true) {
    const thinking = addMsg('sys', S.statusInterviewerThinking);
    try {
        const reply = await callClaude(INTERVIEW_SYSTEM, chat, 1500);
        thinking.remove();
        chat.push({ role: 'assistant', content: reply });
        addMsg('ai', reply);
        if (voiceOn)
            speak(reply, autoListen && sttSupported ? beginListening : undefined);
    }
    catch (e) {
        thinking.remove();
        $('chatErr').textContent = e.message;
    }
}
export async function startInterview() {
    $('chatErr').textContent = '';
    if (!$('apiKey').value.trim()) {
        $('chatErr').textContent = S.errNoKeyInterview;
        return;
    }
    $('chatBox').innerHTML = '';
    chat = [{ role: 'user', content: S.interviewOpener }];
    interviewOn = true;
    $('chatInput').disabled = false;
    $('sendBtn').disabled = false;
    $('verdictBtn').disabled = false;
    const mic = document.getElementById('micBtn');
    if (mic)
        mic.disabled = false;
    $('startBtn').textContent = S.btnRestartInterview;
    addMsg('user', S.interviewOpenerMsg);
    await agentTurn();
}
export async function sendAnswer() {
    if (!interviewOn)
        return;
    const val = $('chatInput').value.trim();
    if (!val)
        return;
    $('chatInput').value = '';
    $('chatErr').textContent = '';
    chat.push({ role: 'user', content: val });
    addMsg('user', val);
    $('sendBtn').disabled = true;
    await agentTurn();
    $('sendBtn').disabled = false;
}
export async function requestVerdict() {
    if (!interviewOn)
        return;
    $('chatErr').textContent = '';
    chat.push({ role: 'user', content: '___VERDICT___' });
    addMsg('sys', S.statusGeneratingVerdict);
    $('sendBtn').disabled = true;
    $('verdictBtn').disabled = true;
    await agentTurn(false); // read the verdict aloud but don't auto-listen after it
    $('verdictBtn').disabled = false;
    $('sendBtn').disabled = false;
}
/* Add the voice controls (a TTS on/off toggle + a mic button) and wire input. */
function buildVoiceControls() {
    const setVoiceLabel = (btn) => { btn.textContent = voiceOn ? S.voiceModeOn : S.voiceModeOff; btn.setAttribute('aria-pressed', String(voiceOn)); };
    if (ttsSupported) {
        const voiceBtn = document.createElement('button');
        voiceBtn.type = 'button';
        voiceBtn.className = 'ghost';
        voiceBtn.id = 'voiceBtn';
        setVoiceLabel(voiceBtn);
        voiceBtn.addEventListener('click', () => {
            voiceOn = !voiceOn;
            localStorage.setItem('ata_voice', voiceOn ? '1' : '');
            if (!voiceOn)
                stopSpeaking();
            setVoiceLabel(voiceBtn);
        });
        $('verdictBtn').after(voiceBtn);
    }
    if (sttSupported) {
        const mic = document.createElement('button');
        mic.type = 'button';
        mic.className = 'primary mic-btn';
        mic.id = 'micBtn';
        mic.textContent = '🎙️';
        mic.title = S.micTitle;
        mic.setAttribute('aria-label', S.micTitle);
        mic.disabled = true;
        mic.addEventListener('click', beginListening);
        $('sendBtn').before(mic);
    }
}
/* Enter (without Shift) submits the current answer. */
export function initInterview() {
    $('chatInput').addEventListener('keydown', e => {
        const ev = e;
        if (ev.key === 'Enter' && !ev.shiftKey) {
            ev.preventDefault();
            sendAnswer();
        }
    });
    buildVoiceControls();
}
