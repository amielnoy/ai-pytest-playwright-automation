# Narration Script — "Why UI Test Suites Die" (intro-automation.mp4, 75s)

Style: Veritasium's curious, direct-to-camera storytelling × Kurzgesagt's warm, reassuring pacing.
Read calmly, slightly slower than feels natural. Pauses marked with (…).

| Time | Scene | Narration |
|---|---|---|
| 0:00–0:05 | Hook | "Most UI test suites are dead within a year of being written. (…) Not because the tests were wrong. Because of something much sneakier." |
| 0:05–0:13 | Naive code | "This is how almost everyone starts — and honestly, it feels great. You tell the browser: click *this* button, fill *this* field. Selectors, everywhere. What could go wrong?" |
| 0:13–0:20 | Collapse | "Then one developer renames one button. (…) Forty-three tests fail. Nothing is actually broken — but your suite is screaming. This is the moment most teams give up on automation." |
| 0:20–0:25 | Question | "But wait. What if a test never touched a selector… at all?" |
| 0:25–0:35 | Real test | "This is a real test from a real project. Read it. It's just… what a user does. Open the site. Go to registration. Fill the form. No URLs. No clicks. No selectors. So — where did they go?" |
| 0:35–0:43 | Architecture | "Here's the trick: one layer in between. The test describes behavior. The page object — one class per page — is where every selector lives. Exactly once. And Playwright drives the actual browser underneath." |
| 0:43–0:50 | The fix | "Now rename that button again. (…) One line changes, in one file. All forty-three tests survive. That's the entire difference between a suite that dies and one that lasts years." |
| 0:50–1:00 | Isolation | "Two more ideas make it bulletproof. Every test gets a brand-new browser profile — no cookies, no leftover state, run them in any order. And that little {ts} in the email? A timestamp. Every run registers a truly new user. An entire species of flaky failures — extinct." |
| 1:00–1:07 | Takeaway | "So UI tests don't die because websites change. Websites always change. They die because selectors live in the wrong place." |
| 1:07–1:15 | Outro | "The full written tutorial — and the real code — are linked below. Build it once, and your tests outlive the redesigns. (…) See you in the next one." |

## Recording options

1. **Record yourself** over the video (QuickTime / OBS), then merge:
   `ffmpeg -i intro-automation.mp4 -i voice.m4a -c:v copy -map 0:v -map 1:a -shortest intro-automation-narrated.mp4`
2. **AI voice** — paste each line into ElevenLabs / OpenAI TTS (`tts-1`, voice "onyx") / Gemini TTS, export one track, merge as above.
