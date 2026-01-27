# Video Analyzer – Unlock Insights from Your Videos

> **Status:** Draft – initial contribution by @ochoaughini  
> This page introduces a reference application that demonstrates how to use the Gemini API to transcribe, summarise and search video content. 

## What the app does

* Drag-and-drop a local video (mp4 / mov / webm).  
* Automatically extracts audio → **speech-to-text** using Gemini audio transcription.  
* Captures still frames every *N* seconds and sends them to Gemini **multimodal** endpoint for scene description.  
* Generates:  
  * An SRT subtitle file.  
  * A bullet-point **summary** (topics, key moments).  
  * Embeddings index allowing **semantic search** over the transcript.

## Quick start

```bash
pip install google-generativeai moviepy ffmpeg-python
python video_analyzer.py --input my_video.mp4 --model gemini-pro-vision
```

The script will write:

* `my_video.srt` – subtitles
* `my_video.summary.txt` – text summary
* `my_video.index.json` – embedding index for search

## Core code snippets

### 1 · Extract audio and transcribe
```python
import google.generativeai as genai
from moviepy.editor import VideoFileClip

audio_path = "tmp_audio.mp3"
VideoFileClip(video_path).audio.write_audiofile(audio_path, logger=None)

model = genai.GenerativeModel("gemini-pro")
transcription = model.generate_content(Path(audio_path).read_bytes(), mime_type="audio/mpeg")
```

### 2 · Describe video frames
```python
from pathlib import Path
from PIL import Image

def sample_frames(video_path, every_sec=5):
    clip = VideoFileClip(video_path)
    for t in range(0, int(clip.duration), every_sec):
        frame = clip.get_frame(t)
        img = Image.fromarray(frame)
        fname = f"frame_{t:04}.png"
        img.save(fname)
        yield fname

vision_model = genai.GenerativeModel("gemini-pro-vision")

scene_descriptions = []
for frame_file in sample_frames(video_path):
    desc = vision_model.generate_content(Path(frame_file).read_bytes(), mime_type="image/png")
    scene_descriptions.append(desc.text)
```

### 3 · Summarise and index
```python
summary = model.generate_content(
    "Summarise this transcript:\n" + transcription.text
).text

embeddings = model.embed_content(transcription.text.split("\n"))
```

## Folder layout
```
video-analyzer/
├── video_analyzer.py        # main script
├── templates/               # optional web UI
└── README.md                # setup & usage docs
```

## Next steps
* Add a Streamlit front-end.  
* Integrate **Gemini function-calling** for automatic action extraction.  
* Accept YouTube URLs (download + analyse).

---
**Contributing** – please feel free to open issues or PRs to improve this example.
