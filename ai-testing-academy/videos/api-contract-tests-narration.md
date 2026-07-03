# Narration Script — "API & Contract Tests" (api-contract-tests.mp4, ~75s)

Style: Veritasium's curious, direct-to-camera storytelling × Kurzgesagt's warm, reassuring pacing.
Read calmly, slightly slower than feels natural. Pauses marked with (…).

| Time | Scene | Narration |
|---|---|---|
| 0:00–0:06 | Hook | "Your UI tests are slow, and they break for reasons that have nothing to do with the thing you're testing. (…) What if most of them didn't need a browser at all?" |
| 0:06–0:15 | The pyramid | "Here's the test pyramid. UI tests sit at the top — few, slow, expensive. Underneath them: API tests. Faster, steadier, and they cover far more of your logic per second." |
| 0:15–0:25 | No raw requests | "But there's a rule. Tests never call `requests` directly. Every call goes through a service layer — `rest_client` for retries and timeouts, and a service class per endpoint. Change the API in one place, not in fifty tests." |
| 0:25–0:35 | Data-driven | "One test shape, many inputs. Parametrize the query — MacBook, iPhone, Samsung — and one function becomes a dozen cases. No copy-paste. And no hard-coded status codes: they live in one constants file." |
| 0:35–0:47 | Contract tests | "Now the quiet hero: contract tests. They don't check *behavior* — they check *shape*. Is the status code right? Are the required fields present? Do product IDs and prices actually parse? Map-driven: one assertion shape across many endpoints." |
| 0:47–0:57 | Why it matters | "When the backend changes a field name or drops a value, a contract test fails instantly — with a clear reason — long before a UI test would flake and leave you guessing." |
| 0:57–1:05 | The payoff | "So push coverage down the pyramid. Let the API layer carry the load, let contracts guard the shape, and keep the browser for the few flows that truly need it." |
| 1:05–1:15 | Outro | "Fast where it can be, thorough where it must be. (…) The real services and tests are linked below. See you in the next one." |

## Recording options

1. **Record the animated explainer** — open `videos/api-contract-tests.html`, press ▶, and screen-record
   (macOS: Cmd+Shift+5, or OBS). Then, if needed, convert/trim with ffmpeg.
2. **Add voice** — paste each line into ElevenLabs / OpenAI TTS (`tts-1`, voice "onyx") / Gemini TTS,
   export one track, and merge:
   `ffmpeg -i api-contract-tests.mp4 -i voice.m4a -c:v copy -map 0:v -map 1:a -shortest api-contract-tests-narrated.mp4`
