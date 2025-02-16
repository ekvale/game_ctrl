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
    audio_generator = client.text_to_speech.convert(
        text=script,
        voice_id="Adam",
        model_id="eleven_monolingual_v1",
        output_format="mp3_44100_128"
    )

    # Convert generator to bytes
    audio_bytes = b''.join(audio_generator)

    # Save the audio
    audio_path = "static/audio/marketing/promo.mp3"
    with open(audio_path, 'wb') as f:
        f.write(audio_bytes)
    
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

def run_test_mode():
    """Run in test mode without using API tokens"""
    print("Running in TEST MODE - no tokens will be used")
    
    # Create test directories
    os.makedirs('static/video/test_assets', exist_ok=True)
    os.makedirs('static/audio/test_assets', exist_ok=True)
    
    # Create sample video files if they don't exist
    test_videos = [
        'static/video/test_assets/sample_intro.mp4',
        'static/video/test_assets/sample_product.mp4',
        'static/video/test_assets/sample_tournament.mp4'
    ]
    
    # Generate test videos using ffmpeg
    for video in test_videos:
        print(f"Creating test video: {video}")
        # Create a 5-second test video with solid color and text
        cmd = (
            f'ffmpeg -y -f lavfi -i color=c=blue:s=1280x720:d=5 '
            f'-vf "drawtext=text=Test Video:fontsize=60:fontcolor=white:x=(w-text_w)/2:y=(h-text_h)/2" '
            f'-c:v libx264 -preset medium -pix_fmt yuv420p {video}'
        )
        print(f"Running command: {cmd}")
        result = os.system(cmd)
        if result != 0:
            raise Exception(f"Failed to create test video: {video}")
        if not os.path.exists(video):
            raise Exception(f"Test video was not created: {video}")
        print(f"Created test video: {video} (size: {os.path.getsize(video)} bytes)")
    
    # Create test audio file
    test_audio = 'static/audio/test_assets/sample_voice.mp3'
    print(f"Creating test audio: {test_audio}")
    # Create a 5-second test audio tone
    cmd = f'ffmpeg -y -f lavfi -i "sine=frequency=440:duration=5" -c:a libmp3lame {test_audio}'
    print(f"Running command: {cmd}")
    result = os.system(cmd)
    if result != 0:
        raise Exception(f"Failed to create test audio: {test_audio}")
    if not os.path.exists(test_audio):
        raise Exception(f"Test audio was not created: {test_audio}")
    print(f"Created test audio: {test_audio} (size: {os.path.getsize(test_audio)} bytes)")
    
    # Copy test files to temp and marketing directories
    video_paths = []
    for i, video in enumerate(test_videos):
        output_path = f'static/video/temp/test_{i}.mp4'
        print(f"Copying {video} to {output_path}")
        os.system(f'cp {video} {output_path}')
        if not os.path.exists(output_path):
            raise Exception(f"Failed to copy video to {output_path}")
        video_paths.append(output_path)
        print(f"Copied video to {output_path} (size: {os.path.getsize(output_path)} bytes)")
    
    audio_path = 'static/audio/marketing/test_promo.mp3'
    print(f"Copying {test_audio} to {audio_path}")
    os.system(f'cp {test_audio} {audio_path}')
    if not os.path.exists(audio_path):
        raise Exception(f"Failed to copy audio to {audio_path}")
    print(f"Copied audio to {audio_path} (size: {os.path.getsize(audio_path)} bytes)")
    
    return video_paths, audio_path

def main(test=False):
    video_paths = []
    try:
        # Setup directories
        setup_directories()
        
        if test:
            # Run in test mode
            video_paths, audio_path = run_test_mode()
            final_path = create_final_video(video_paths, audio_path)
            print(f"Test video created successfully at {final_path}")
        else:
            # Normal mode with API calls
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
    import sys
    is_test_mode = "--test" in sys.argv
    main(test=is_test_mode)
