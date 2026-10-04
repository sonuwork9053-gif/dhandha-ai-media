# Dhandha AI — production runbook

Channel: Dhandha AI (@dhandhaai), channel ID `UC8ctVutqcPP7NTxzPQjazZQ`.
Niche: AI for small business owners. Each video = one real business task done with a real, working tool, shown on screen.
Owner's standing instruction (3 Oct 2026): publish directly as public, no approval step.

## Rules
- Build a real working tool first and test it. The video shows that tool, nothing mocked.
- Never invent a number, a result or a source. On-screen data is sample data and is labelled "Sample data".
- Hindi narration (Devanagari text for TTS). Description says the narration is an AI voice.
- Title and thumbnail carry different words. Thumbnail: navy `#0B1220`, yellow `#FFC400`, max 4 words big.
- Look at a contact sheet of frames before uploading. Fix overlaps and cut-off text first.
- Audio cannot be listened to from the workspace. Say so in the run report. The owner chose the Kokoro voice 'hm_omega' on 4 Oct 2026 (Pratham and Rohan are approved fallbacks).

## Pipeline (current, tested end to end on video 02 — free voice, no ElevenLabs)
ElevenLabs is NOT used any more: the owner's free ElevenLabs account was disabled on 3 Oct 2026. Do not call ElevenLabs tools.

0. Voice model (data files, not kept in this repo). The owner chose the Kokoro voice **hm_omega** on 4 Oct 2026:
   `curl -sSL -o /tmp/kokoro.tar.bz2 https://github.com/k2-fsa/sherpa-onnx/releases/download/tts-models/kokoro-multi-lang-v1_0.tar.bz2 && tar xjf /tmp/kokoro.tar.bz2 -C /tmp` (350 MB)
   Use `KokoroVoice("/tmp/kokoro-multi-lang-v1_0", "hm_omega", speed=1.2)` from `kit/hindi_tts.py` (24 kHz, own phonemizer, pre-installed `onnxruntime`). Speed 1.2 brings its pace close to the earlier narration; keep sec-per-beat sensible.
   Fallback if Kokoro cannot be downloaded or fails: Piper voice Pratham — `curl -sSL -o /tmp/pratham.tar.bz2 https://github.com/k2-fsa/sherpa-onnx/releases/download/tts-models/vits-piper-hi_IN-pratham-medium.tar.bz2 && tar xjf /tmp/pratham.tar.bz2 -C /tmp`, then `Voice("/tmp/vits-piper-hi_IN-pratham-medium/hi_IN-pratham-medium.onnx")`.
   Do NOT run the Piper binary or any other downloaded program — that is blocked. If `onnxruntime` is missing or no model can be downloaded, stop and report.
1. Build the tool as a single HTML file in `video-NN/src/`, test with Playwright (see `video-02/src/test.py`).
2. Write the script: 5 hooks scored with `hookscore.py` (repo Jakeschincariol/youtube-agent-skill, `skills/yt-script`), keep the best, then about 10 beats. Save the beats as `video-NN/src/beats.json` (Devanagari; spell numbers in words; English words are handled by `LATIN`/`SPOKEN` in `kit/hindi_tts.py` — add new ones there).
3. Narration: `voice.narrate(beats, "narr.wav")` returns the EXACT seconds of every beat. Save them as `dur.json`. Check `V.missing` is empty and print `phonemize()` of a few lines to sanity-check pronunciation.
4. Record with `kit/director.py` `Stage(html, beats, total, out, init_js, durations=dur, zoom=1.36, maxw=1350)` — see `video-03/src/record.py` (the current reference). Pick zoom/maxw so the tool fills the screen, text is readable on a phone, and every row fits above the caption. Exact durations mean captions and voice stay in sync.
5. Master the voice, then join: `ffmpeg -i narr.wav -af "highpass=f=70,acompressor=threshold=-20dB:ratio=3:attack=5:release=80:makeup=2,loudnorm=I=-14:TP=-1.5:LRA=9" -ar 48000 narr-m.wav` and `ffmpeg -i silent.mp4 -i narr-m.wav -c:v copy -c:a aac -b:a 160k -shortest -movflags +faststart video-NN/video-hi.mp4`.
6. Look at a contact sheet of frames (one per beat). Fix overlaps or cut-off text and re-record.
7. Thumbnail `video-NN/thumb.jpg` (see `video-02/src/thumb.html`).
8. Publish the tool page (`tools/<slug>.html`, add to `index.html`), commit everything except wav/silent files, push to `main`.
9. Confirm the tool page URL loads, then Zapier YouTube `upload_video`: `video` = `https://raw.githubusercontent.com/sonuwork9053-gif/dhandha-ai-media/main/video-NN/video-hi.mp4`, `thumbnail` = the raw URL of thumb.jpg, `privacy_status: public`, `category_id: "28"`, `default_language: hi`, `default_audio_language: hi`, `made_for_kids: false`. Chapters in the description come from the exact beat durations (each chapter at least 10 seconds).
10. Zapier YouTube raw requests: add to playlist `PLVDr12VSeYo4` (POST playlistItems), add English localization (PUT videos?part=localizations), post one channel comment with a question (POST commentThreads).
11. Tick the topic in `TOPICS.md` with the links, commit, push.

The workspace cannot reach YouTube directly; GitHub raw URLs are how files reach Zapier.

## Shorts
- One Short per long video: vertical 1080x1920, under 40 seconds, 4 beats: hook, what the tool shows, the one key action, end card pointing to the full video on the channel.
- Separate short Hindi narration made with `kit/hindi_tts.py` (exact durations). Record vertically with `video-01/src/short.py` as the layout reference (top caption band, spotlight, panel) but drive the beat timing from the exact durations, join audio with ffmpeg, push `video-NN/short-hi.mp4`, upload from the raw GitHub URL.
- Title ends with `#Shorts`. Description: one line plus the full video link.

## Topics and variety (owner's instruction, 3 Oct 2026)
- Choose the topic yourself. Every video uses a different kind of small business as its example (RO service, kirana shop, tailor, coaching class, salon, medical store, tiffin service, mobile repair, hardware shop, photographer...). Do not repeat the same business type two days in a row.
- The example is an illustrative scenario with sample data. Never present it as a real customer's story or claim real results.
- When TOPICS.md runs out, add ten new topics in the same style and continue.
- Goal: reach YouTube Partner Program thresholds as fast as honestly possible. No bought views, sub4sub or link spam.

## Free tool page for every video (owner enabled GitHub Pages on 3 Oct 2026)
- Copy each video's tool to `tools/<slug>.html` with the small "Free tool by Dhandha AI" credit line (see `tools/follow-up-register.html`), add it to the list in `index.html`, commit and push.
- Live URL pattern: `https://sonuwork9053-gif.github.io/dhandha-ai-media/tools/<slug>.html`. Pages takes a few minutes to deploy; fetch the URL and confirm it loads before putting it in a description. Never publish a dead link.
- First line of every description (Hindi and the English localization): the free tool link.
- Add each long video to playlist `PLVDr12VSeYo4`, add an English title/description localization, and post one channel comment that asks viewers a question.

## Length, format and Shorts (owner's instruction, 4 Oct 2026)
- Goal: qualify for the YouTube Partner Program under the current thresholds (1,000 subscribers + 4,000 watch hours, or 10M Shorts views in 90 days) before the entry bar is reported to rise on 1 Feb 2027. Watch hours need longer videos.
- Grow length step by step: videos 03–06 about 3 minutes (14 beats), then 4–5 minutes, and from the second week one 8–10 minute "poora setup" episode per week that combines related tools for one kind of shop (for example kirana: udhaar khata + galla register + stock list). Never pad: every added minute must show something new on screen.
- Cut 2–3 Shorts from every long video (hook, the one key action, the before/after), each with its own short narration.
- Avoid a template feel (YouTube rejects repetitive, mass-produced channels): rotate the story format between videos (a "maan lijiye" story, a mistake to avoid, a before/after, a viewer's request, a comparison), vary the thumbnail layout and the caption wording, use a different business each time, and include at least one scene per video that is not the tool (a story panel, a comparison, a list of who else can use it).
- Do not have the narrator give tax, legal, medical or investment advice.
- The owner deleted the first udhaar-khata video (Pratham voice, small text). Quality bar: Omega voice, large readable tool, a real story.
