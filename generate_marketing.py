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

def download_video(url, output_path):
    """Download video from URL"""
    response = requests.get(url, stream=True)
    with open(output_path, 'wb') as f:
        for chunk in response.iter_content(chunk_size=8192):
            f.write(chunk)

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
        print(f"Video saved to {output_path}")
    else:
        raise Exception("No video URL received from Replicate")

def generate_audio():
    """Generate audio using ElevenLabs"""
    script = """Welcome to GamesCtrls, where precision meets passion.
    Introducing our professional-grade controller lineup, designed for every type of player."""

    # Generate audio using the correct API
    audio = client.text_to_speech.convert(
        text=script,
        voice_id="Adam",  # You might need to use the actual voice ID
        model_id="eleven_monolingual_v1",
        output_format="mp3_44100_128"
    )

    # Save the audio
    audio_path = "static/audio/marketing/promo.mp3"
    with open(audio_path, 'wb') as f:
        f.write(audio)
    
    return audio_path

# ... rest of the code remains the same ...def download_video(url, output_path):
    """Download video from URL"""
    response = requests.get(url, stream=True)
    with open(output_path, 'wb') as f:
        for chunk in response.iter_content(chunk_size=8192):
            f.write(chunk)

def generate_video_segment(prompt, output_path, duration_seconds=5):
    """Generate a video segment using Replicate"""
    print(f"Generating video for prompt: {prompt}")
    
    output = replicate.run(
        "anotherjesse/zeroscope-v2-xl:9f747673945c62801b13b84701c783929c0ee784e4748ec062204894dda1a351",
        input={
            "prompt": prompt,
            "fps": 24,
            "num_frames": duration_seconds * 24,  # Convert seconds to frames
            "guidance_scale": 17.5,  # Higher value for more prompt-adherent results
            "num_inference_steps": 50  # Higher value for better quality
        }
    )
    
    if isinstance(output, list) and output:
        download_video(output[0], output_path)
        print(f"Video saved to {output_path}")
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

    # Generate audio using the new API
    audio = client.generate(
        text=script,
        voice="Adam",
        model="eleven_monolingual_v1"
    )

    # Save the audio
    audio_path = "static/audio/marketing/promo.mp3"
    with open(audio_path, 'wb') as f:
        f.write(audio)
    
    return audio_path

def create_final_video(video_paths, audio_path):
    """Combine video segments and add audio"""
    # Load video clips
    clips = [VideoFileClip(path) for path in video_paths]
    
    # Concatenate videos
    final_video = concatenate_videoclips(clips)
    
    # Add audio
    audio = AudioFileClip(audio_path)
    
    # If audio is longer than video, extend video duration
    if audio.duration > final_video.duration:
        final_video = final_video.loop(duration=audio.duration)
    
    # Add audio to video
    final_video = final_video.set_audio(audio)
    
    # Write final video
    output_path = "static/video/marketing/final_promo.mp4"
    final_video.write_videofile(
        output_path,
        codec='libx264',
        audio_codec='aac',
        fps=24
    )
    return output_path

def main():
    # Create directories
    os.makedirs('static/video/temp', exist_ok=True)
    os.makedirs('static/video/marketing', exist_ok=True)
    os.makedirs('static/audio/marketing', exist_ok=True)

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

    try:
        # Generate video segments
        video_paths = []
        for segment in segments:
            generate_video_segment(segment["prompt"], segment["output"])
            video_paths.append(segment["output"])

        # Generate audio
        print("Generating audio...")
        audio_path = generate_audio()

        # Combine videos and add audio
        print("Creating final video...")
        final_path = create_final_video(video_paths, audio_path)
        
        print(f"Marketing video created successfully at {final_path}")

    except Exception as e:
        print(f"Error: {str(e)}")
    finally:
        # Clean up temp files
        print("Cleaning up temporary files...")
        for path in video_paths:
            if os.path.exists(path):
                os.remove(path)

if __name__ == "__main__":
    main()
