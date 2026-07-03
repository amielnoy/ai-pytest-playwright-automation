/* Agent 2 — interview readiness: a five-stage mock interview with a verdict. */
import type { Msg } from './types.js';
import { $ } from './dom.js';
import { L, S } from './i18n.js';
import { callClaude } from './providers.js';

const INTERVIEW_SYSTEM = L.prompts.interview;

let chat: Msg[] = [];
let interviewOn = false;

function addMsg(cls: string, text: string): HTMLDivElement {
  const div = document.createElement('div');
  div.className = 'msg ' + cls;
  div.textContent = text;
  const box = $('chatBox');
  box.appendChild(div);
  box.scrollTop = box.scrollHeight;
  return div;
}

async function agentTurn(): Promise<void> {
  const thinking = addMsg('sys', S.statusInterviewerThinking);
  try {
    const reply = await callClaude(INTERVIEW_SYSTEM, chat, 1500);
    thinking.remove();
    chat.push({ role: 'assistant', content: reply });
    addMsg('ai', reply);
  } catch (e) {
    thinking.remove();
    $('chatErr').textContent = (e as Error).message;
  }
}

export async function startInterview(): Promise<void> {
  $('chatErr').textContent = '';
  if (!$('apiKey').value.trim()) { $('chatErr').textContent = S.errNoKeyInterview; return; }
  $('chatBox').innerHTML = '';
  chat = [{ role: 'user', content: S.interviewOpener }];
  interviewOn = true;
  $('chatInput').disabled = false; $('sendBtn').disabled = false; $('verdictBtn').disabled = false;
  $('startBtn').textContent = S.btnRestartInterview;
  addMsg('user', S.interviewOpenerMsg);
  await agentTurn();
}

export async function sendAnswer(): Promise<void> {
  if (!interviewOn) return;
  const val = $('chatInput').value.trim();
  if (!val) return;
  $('chatInput').value = '';
  $('chatErr').textContent = '';
  chat.push({ role: 'user', content: val });
  addMsg('user', val);
  $('sendBtn').disabled = true;
  await agentTurn();
  $('sendBtn').disabled = false;
}

export async function requestVerdict(): Promise<void> {
  if (!interviewOn) return;
  $('chatErr').textContent = '';
  chat.push({ role: 'user', content: '___VERDICT___' });
  addMsg('sys', S.statusGeneratingVerdict);
  $('sendBtn').disabled = true; $('verdictBtn').disabled = true;
  await agentTurn();
  $('verdictBtn').disabled = false; $('sendBtn').disabled = false;
}

/* Enter (without Shift) submits the current answer. */
export function initInterview(): void {
  $('chatInput').addEventListener('keydown', e => {
    const ev = e as KeyboardEvent;
    if (ev.key === 'Enter' && !ev.shiftKey) { ev.preventDefault(); sendAnswer(); }
  });
}
