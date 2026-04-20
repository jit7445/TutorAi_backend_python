import os
from gtts import gTTS
from PIL import Image, ImageDraw, ImageFont
import textwrap
import subprocess

def generate_video(notes_data: dict, output_dir: str) -> dict:
    os.makedirs(output_dir, exist_ok=True)
    topic = notes_data.get("topic", "Topic")
    notes = notes_data.get("notes", [])
    
    video_path = os.path.join(output_dir, "output.mp4")
    
    # Text to speech
    script = f"Topic: {topic}. " + " ".join(notes)
    audio_path = os.path.join(output_dir, "audio.mp3")
    
    tts = gTTS(text=script, lang='en')
    tts.save(audio_path)
    
    # Generate simple slide
    slide_path = os.path.join(output_dir, "slide.png")
    img = Image.new('RGB', (1280, 720), color = (73, 109, 137))
    d = ImageDraw.Draw(img)
    
    try:
        font_title = ImageFont.truetype("Arial.ttf", 60)
        font_text = ImageFont.truetype("Arial.ttf", 36)
    except:
        try:
            # Fallback for Mac
            font_title = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 60)
            font_text = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 36)
        except:
            font_title = ImageFont.load_default()
            font_text = ImageFont.load_default()
        
    wrapper_title = textwrap.TextWrapper(width=40)
    topic_text = wrapper_title.fill(text=topic)
    
    # Draw Topic Title
    d.text((100, 100), topic_text, fill=(255, 255, 0), font=font_title)
    
    # Draw Notes Iteratively
    wrapper_notes = textwrap.TextWrapper(width=60)
    y_offset = 200
    for note in notes:
        wrapped_note = wrapper_notes.fill(text=note)
        # Make it a bullet point
        d.text((100, y_offset), f"• {wrapped_note}", fill=(255, 255, 255), font=font_text)
        
        # Calculate next line position based on number of wrapped lines
        lines = wrapped_note.count('\n') + 1
        y_offset += (lines * 50) + 20
    img.save(slide_path)
    
    # Combine using bundled FFmpeg
    import imageio_ffmpeg
    ffmpeg_exe = imageio_ffmpeg.get_ffmpeg_exe()
    
    try:
        cmd = [
            ffmpeg_exe, "-y", "-loop", "1", "-i", slide_path, "-i", audio_path,
            "-c:v", "libx264", "-c:a", "aac", "-b:a", "192k", "-pix_fmt", "yuv420p",
            "-shortest", video_path
        ]
        subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    except Exception as e:
        print(f"Video generation error: {e}")
        # Return fallback or raise
        raise e
        
    return {"video_path": video_path}
