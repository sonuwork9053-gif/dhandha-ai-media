# Topic queue

Take the first unchecked topic. After publishing, tick it and add the video links. Each topic names the business used as the example; keep the business different from the previous video.

- [x] 01 RO service: customer follow-up register with WhatsApp reminders — https://www.youtube.com/watch?v=kicWp8y8u8Y (Short: https://www.youtube.com/watch?v=vYfSIGHQaAY)
- [x] 02 Kirana shop: udhaar khata, redone 4 Oct as "teen galtiyan" (larger tool, frame-accurate recorder) — https://www.youtube.com/watch?v=9QTCPuKDQjk (Short: https://www.youtube.com/watch?v=WSveGr-Gd8w). Voice: Pratham source voice (owner's reference file was not in the repo, so no conversion). Hooks were written against the formulas but not scored: running hookscore.py was blocked in that session.
- [x] 03 Tailor / boutique: order register — https://www.youtube.com/watch?v=BHRajvVMvDw (Short 1 built 4 Oct (`video-03/src/short.py`) but NOT uploaded: waiting for the owner to say whether his cloned voice sounds right; as published, video 03's picture runs up to 3.5 s behind the voice in the second half (old recorder))
- [ ] 04 Coaching class: fees due register with monthly reminder — BUILT 5 Oct, NOT uploaded: Zapier returned "task limit reached for the current billing period" on upload_video (and on every later YouTube call). Ready files: `video-04/video-hi.mp4` (3:29), `video-04/short-hi.mp4` (27 s), `video-04/thumb.jpg`, tool page `tools/fees-register.html` (live). Next run: do not rebuild; upload these (title/description/chapters: see `video-04/src/upload.md`), then playlist, English localization, comment, Short, and tick this line. Voice: re-voiced 6 Oct in Kokoro hf_beta (owner's choice), 3:51. Hooks written but not scored (hookscore.py not available in the session). 6 Oct run: Zapier still returned the same task-limit error on the first YouTube calls (commentThreads GET and playlistItems GET), so nothing was uploaded and comments could not be read; nothing new was built.
- [ ] 05 Mobile repair shop: job card and status message for the customer
- [ ] 06 Tiffin service: daily order count and monthly bill per customer
- [ ] 07 Salon: appointment book with reminder message
- [ ] 08 Hardware shop: quotation maker that prints a clean PDF
- [ ] 09 Medical store: stock low and expiry alert list
- [ ] 10 Amazon / Flipkart seller: product listing writer from a few facts
- [ ] 11 Any shop: WhatsApp quick-reply bank for the ten most asked questions
- [ ] 12 Any shop: daily galla register — sale, kharcha, bachat

## Pending fix (do after the day's video, only if the upload is not throttled)
- Video 03 `BHRajvVMvDw` has the picture up to 3.5 s behind the voice. Corrected file: `video-03/video-hi-v2.mp4`. Upload it with the same title/description/tags/thumbnail (`notify_subscribers: false`), add to the playlist, add the English localization, then delete `BHRajvVMvDw` and remove this note. First try on 4 Oct was throttled by Zapier.
