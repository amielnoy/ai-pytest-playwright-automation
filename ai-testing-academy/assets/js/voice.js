/* Web Speech API wrappers for the interview: text-to-speech for the interviewer's
   questions, speech-to-text for the candidate's answers. Both are browser-native
   (no API key, no cost). STT (SpeechRecognition) is Chrome/Edge only; TTS is broad. */
import { activeLang } from './i18n.js';
const LANG = activeLang === 'he' ? 'he-IL' : 'en-US';
const synth = window.speechSynthesis;
const Recognition = window.SpeechRecognition || window.webkitSpeechRecognition;
export const ttsSupported = !!synth;
export const sttSupported = !!Recognition;
/* Speak text in the active language; onEnd fires when speech finishes (or immediately if unsupported). */
export function speak(text, onEnd) {
    if (!synth) {
        onEnd?.();
        return;
    }
    synth.cancel();
    const u = new SpeechSynthesisUtterance(text);
    u.lang = LANG;
    if (onEnd)
        u.onend = () => onEnd();
    synth.speak(u);
}
export function stopSpeaking() { synth?.cancel(); }
let rec = null;
/* Toggle speech recognition: onFinal gets the transcript, onState(listening) drives the UI. */
export function toggleRecognition(onFinal, onState) {
    if (!Recognition)
        return;
    if (rec) {
        rec.stop();
        return;
    } // a second tap stops listening
    stopSpeaking(); // barge-in over a question being read
    rec = new Recognition();
    rec.lang = LANG;
    rec.interimResults = false;
    rec.maxAlternatives = 1;
    rec.onresult = (e) => onFinal(e.results[0][0].transcript);
    rec.onend = () => { rec = null; onState(false); };
    rec.onerror = () => { rec = null; onState(false); };
    onState(true);
    try {
        rec.start();
    }
    catch {
        rec = null;
        onState(false);
    }
}
export function isListening() { return !!rec; }
