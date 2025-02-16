import os
import replicate
import requests
from dotenv import load_dotenv
from elevenlabs.client import ElevenLabs
from moviepy.editor import VideoFileClip, AudioFileClip, concatenate_videoclips

# Load environment variables
load_dotenv('.env.prod')

# Set API keys
elevenlabs_key = os.getenv('ELEVENLABS_API_KEY')
replicate_key = os.getenv('REPLICATE_API_KEY')
client = ElevenLabs(api_key=elevenlabs_key)
os.environ['REPLICATE_API_TOKEN'] = replicate_key

def setup_directories():
    """Create and verify directories"""
    directories = [
        'static/video/temp',
        'static/video/marketing',
        'static/audio/marketing'
    ]
    for directory in directories:
        os.makedirs(directory, exist_ok=True)
        print(f"Created/verified directory: {directory}")

def download_video(url, output_path):
    """Download video from URL"""
    print(f"Downloading video from {url}")
    response = requests.get(url, stream=True)
    with open(output_path, 'wb') as f:
        for chunk in response.iter_content(chunk_size=8192):
            f.write(chunk)
    
    # Verify download
    if os.path.exists(output_path) and os.path.getsize(output_path) > 0:
        print(f"Successfully downloaded video to {output_path}")
        print(f"File size: {os.path.getsize(output_path)} bytes")
    else:
        raise Exception(f"Failed to download video to {output_path}")

def generate_video_segment(prompt, output_path, duration_seconds=5):
    """Generate a video segment using Replicate"""
    print(f"Generating video for prompt: {prompt}")
    
    output = replicate.run(
        "anotherjesse/zeroscope-v2-xl:9f747673945c62801b13b84701c783929c0ee784e4748ec062204894dda1a351",
        input={
            "prompt": prompt,
            "fps": 24,
            "num_frames": duration_seconds * 24,
            "guidance_scale": 17.5,
            "num_inference_steps": 50
        }
    )
    
    if isinstance(output, list) and output:
        download_video(output[0], output_path)
    else:
        raise Exception("No video URL received from Replicate")

def generate_audio():
    """Generate audio using ElevenLabs"""
    script = """Welcome to GamesCtrls, where precision meets passion.

    Introducing our professional-grade controller lineup, designed for every type of player:

    The Pro Fighter X8 - Our flagship controller, featuring tournament-grade components and customizable LED lighting.

    The Classic Arcade Plus - Experience the nostalgia of arcade gaming with modern reliability.

    And for the competitive scene: The Tournament Edition Pro. Built with premium Sanwa components.

    Visit GamesCtrls.com today and elevate your game to the next level."""

    print("Generating audio...")
    
    # Generate audio using the correct API
    audio = client.text_to_speech.convert(
        text=script,
        voice_id="Adam",
        model_id="eleven_monolingual_v1",
        output_format="mp3_44100_128"
    )

    # Save the audio
    audio_path = "static/audio/marketing/promo.mp3"
    with open(audio_path, 'wb') as f:
        f.write(audio)
    
    # Verify audio file
    if os.path.exists(audio_path) and os.path.getsize(audio_path) > 0:
        print(f"Successfully generated audio at {audio_path}")
        print(f"File size: {os.path.getsize(audio_path)} bytes")
    else:
        raise Exception(f"Failed to generate audio at {audio_path}")
    
    return audio_path

def create_final_video(video_paths, audio_path):
    """Combine video segments and add audio"""
    print("Starting video combination process...")
    
    # Verify input files
    for path in video_paths + [audio_path]:
        if not os.path.exists(path):
            raise FileNotFoundError(f"Input file not found: {path}")
    
    # Load video clips
    clips = [VideoFileClip(path) for path in video_paths]
    print(f"Loaded {len(clips)} video clips")
    
    # Concatenate videos
    final_video = concatenate_videoclips(clips)
    print(f"Combined video duration: {final_video.duration} seconds")
    
    # Add audio
    audio = AudioFileClip(audio_path)
    print(f"Audio duration: {audio.duration} seconds")
    
    # If audio is longer than video, extend video duration
    if audio.duration > final_video.duration:
        final_video = final_video.loop(duration=audio.duration)
    
    # Add audio to video
    final_video = final_video.set_audio(audio)
    
    # Write final video
    output_path = "static/video/marketing/final_promo.mp4"
    print(f"Writing final video to {output_path}")
    
    final_video.write_videofile(
        output_path,
        codec='libx264',
        audio_codec='aac',
        fps=24
    )
    
    # Verify output
    if os.path.exists(output_path) and os.path.getsize(output_path) > 0:
        print(f"Successfully created final video at {output_path}")
        print(f"Final file size: {os.path.getsize(output_path)} bytes")
        return output_path
    else:
        raise Exception("Failed to create final video")

def main():
    video_paths = []
    try:
        # Setup directories
        setup_directories()
        
        # Video segments with prompts
        segments = [
            {
                "prompt": "Professional gaming controller floating in modern studio, dramatic lighting, product showcase, photorealistic, centered composition",
                "output": "static/video/temp/intro.mp4"
            },
            {
                "prompt": "Pro Fighter X8 arcade controller with LED lighting, premium buttons, professional product photography, dramatic lighting",
                "output": "static/video/temp/pro_fighter.mp4"
            },
            {
                "prompt": "Tournament gaming scene with players using arcade controllers, esports environment, dramatic lighting",
                "output": "static/video/temp/tournament.mp4"
            }
        ]

        # Generate video segments
        for segment in segments:
            generate_video_segment(segment["prompt"], segment["output"])
            video_paths.append(segment["output"])
            print(f"Generated segment: {segment['output']}")

        # Generate audio
        audio_path = generate_audio()

        # Combine videos and add audio
        final_path = create_final_video(video_paths, audio_path)
        
        print(f"Marketing video created successfully at {final_path}")

    except Exception as e:
        print(f"Error: {str(e)}")
        raise
    finally:
        # Clean up temp files
        print("Cleaning up temporary files...")
        for path in video_paths:
            if os.path.exists(path):
                os.remove(path)
                print(f"Removed temp file: {path}")

if __name__ == "__main__":
    main()
