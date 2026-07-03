/* Web Speech API wrappers for the interview: text-to-speech for the interviewer's
   questions, speech-to-text for the candidate's answers. Both are browser-native
   (no API key, no cost). STT (SpeechRecognition) is Chrome/Edge only; TTS is broad.

   The recogniser is tuned for real spoken answers: it records for at least 20s and
   tolerates pauses of up to 10s, accumulating every speech segment, and only
   finalises after 10s of silence (past the 20s minimum) or a manual stop. Browsers
   end recognition after a few seconds of silence on their own, so we restart it to
   keep one continuous session within that window. */
import { activeLang } from './i18n.js';

const LANG = activeLang === 'he' ? 'he-IL' : 'en-US';
const synth: SpeechSynthesis | undefined = window.speechSynthesis;
const Recognition: any = (window as any).SpeechRecognition || (window as any).webkitSpeechRecognition;

export const ttsSupported = !!synth;
export const sttSupported = !!Recognition;

const MIN_MS = 20000;    // record for at least 20s before silence can end it
const MAX_PAUSE_MS = 10000;  // finalise after this much continuous silence
const MAX_MS = 180000;   // hard safety cap

/* Speak text in the active language; onEnd fires when speech finishes (or immediately if unsupported). */
export function speak(text: string, onEnd?: () => void): void {
  if (!synth) { onEnd?.(); return; }
  synth.cancel();
  const u = new SpeechSynthesisUtterance(text);
  u.lang = LANG;
  if (onEnd) u.onend = () => onEnd();
  synth.speak(u);
}

export function stopSpeaking(): void { synth?.cancel(); }

let rec: any = null;
let timer: number | null = null;
let transcript = '';
let startedAt = 0;
let lastSpeech = 0;
let finalizing = false;
let onFinalCb: ((t: string) => void) | null = null;
let onStateCb: ((listening: boolean) => void) | null = null;

function clearTimer(): void { if (timer !== null) { clearInterval(timer); timer = null; } }

function deliver(): void {
  clearTimer();
  const text = transcript.trim();
  const cb = onFinalCb, state = onStateCb;
  rec = null; finalizing = false; onFinalCb = null; onStateCb = null;
  state?.(false);
  if (text) cb?.(text);
}

/* Stop listening and deliver the accumulated transcript. */
function finish(): void {
  if (!rec) return;
  finalizing = true;
  clearTimer();
  try { rec.stop(); } catch { deliver(); }   // rec.onend delivers; if stop() throws, deliver now
}

function tick(): void {
  const now = Date.now();
  const elapsed = now - startedAt;
  const silence = now - lastSpeech;
  if (elapsed >= MAX_MS) { finish(); return; }
  if (elapsed >= MIN_MS && silence >= MAX_PAUSE_MS) finish();
}

/* Toggle speech recognition: onFinal gets the full transcript once recording ends,
   onState(listening) drives the UI. A second call while listening stops it early. */
export function toggleRecognition(onFinal: (t: string) => void, onState: (listening: boolean) => void): void {
  if (!Recognition) return;
  if (rec) { finish(); return; }   // a second tap stops and submits
  stopSpeaking();                  // barge-in over a question being read
  transcript = ''; finalizing = false;
  onFinalCb = onFinal; onStateCb = onState;

  rec = new Recognition();
  rec.lang = LANG;
  rec.continuous = true;
  rec.interimResults = true;
  rec.maxAlternatives = 1;
  rec.onresult = (e: any) => {
    lastSpeech = Date.now();
    for (let i = e.resultIndex; i < e.results.length; i++) {
      if (e.results[i].isFinal) transcript += e.results[i][0].transcript + ' ';
    }
  };
  rec.onerror = (ev: any) => {
    if (ev.error === 'not-allowed' || ev.error === 'service-not-allowed') finalizing = true;
    // 'no-speech'/'aborted' just end the session; onend restarts within the window
  };
  rec.onend = () => {
    if (finalizing || Date.now() - startedAt >= MAX_MS) { deliver(); return; }
    try { rec.start(); }               // browser ended early — keep listening
    catch { setTimeout(() => { if (rec && !finalizing) { try { rec.start(); } catch { /* give up */ } } }, 120); }
  };

  startedAt = lastSpeech = Date.now();
  onState(true);
  try { rec.start(); } catch { deliver(); }
  timer = setInterval(tick, 500) as unknown as number;
}

export function isListening(): boolean { return !!rec; }
