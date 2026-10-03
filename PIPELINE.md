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
- Audio cannot be listened to from the workspace. Say so in the run report.

## Pipeline (tested end to end on video 01)
1. Build the tool as a single HTML file in `video-NN/src/`, test with Playwright.
2. Write the script: 5 hooks scored with `hookscore.py` (repo: Jakeschincariol/youtube-agent-skill, `skills/yt-script`), keep the best, then about 10 beats.
3. ElevenLabs `creative_generate_speech`: whole Hindi narration in one call, `generations_count: 1`, model `eleven_multilingual_v2`, voice `zs7UfyHqCCmny7uTxCYi` (Ruhaan). Poll `creative_get_flow_run_status` for `duration_secs`.
4. Record the screen with Playwright (`record_video_dir`, 1920x1080). Beat lengths come from `kit/timing.py` (`beat_durations(beats, total_seconds)`), not from raw character counts: the owner reported captions and voice drifting slightly on video 01, which used character counts. Put each beat's key action in the middle of the beat so a one-second drift does not show. See `video-01/src/record.py` for the director overlay (captions, spotlight, cursor, panels). Convert to mp4 with ffmpeg.
5. Commit `video-NN/screen-hi.mp4` and `video-NN/thumb.jpg` to this repo and push to `main`.
6. ElevenLabs `creative_attach_reference_file` with the raw.githubusercontent.com URL into the same flow as the narration, then `creative_add_flow_node` (`composition`, `eleven_composition`, `connect_from` = video node + TTS node), `creative_run_flow_nodes` with `generations_count: 1`. Poll until completed, take `master_url`.
7. Zapier YouTube `upload_video`: `video` = master_url, `thumbnail` = raw GitHub URL, `privacy_status: public`, `category_id: "28"`, `default_language: hi`, `made_for_kids: false`.
8. Mark the topic done in `TOPICS.md`, commit, push.

The workspace cannot reach ElevenLabs or YouTube directly. GitHub is the only way files leave it.

## Shorts (tested on video 01)
- One Short per long video: vertical 1080x1920, under 40 seconds, 4 beats: hook, what the tool shows, the one key action, end card pointing to the full video on the channel.
- Separate short Hindi narration (one TTS take). Same pipeline as the long video: record with `video-01/src/short.py` as the reference (top caption band, spotlight, panel), push `video-NN/short-hi.mp4`, attach, compose, upload.
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
