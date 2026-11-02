# Demo video

[Watch or download the MP4](customer_support_demo.mp4). Duration: approximately 5 minutes (5:01). Resolution: 1920×1080. Narration: macOS Samantha, a standard synthetic voice. Captions are burned into the video; an SRT file and transcript are also included.

This presentation walks through saved project evidence: reviewed policy, original failures, the 2048-token control, the focused prompt edit, a targeted fix, two regressions, cost and limitations. It does not run new model calls. Inspect the linked LangSmith experiments or saved trace evidence for underlying execution records.

The video is available in GitHub. If the course requires a Loom link, upload this MP4 to an appropriate hosting account and add the URL to the submission. Review the narration before submitting.

Rebuild on macOS with Python 3.12, Pillow and imageio-ffmpeg 0.6.0 installed, and the standard Samantha voice available: `python scripts/build_demo_video.py`. No Fireworks or LangSmith credentials are used. The builder uses `/private/tmp/week4-video` for intermediate audio and frames.
