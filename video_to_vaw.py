import os
from moviepy.editor import VideoFileClip
import logging

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

def create_directories():
    """Create necessary directories if they don't exist."""
    os.makedirs('videos', exist_ok=True)
    os.makedirs('video_audios', exist_ok=True)

def get_video_files():
    """Get list of video files in the videos directory."""
    video_extensions = ('.mp4', '.mov', '.avi', '.mkv', '.wmv', '.flv', '.webm')
    video_files = []
    
    for file in os.listdir('videos'):
        if file.lower().endswith(video_extensions):
            video_files.append(file)
    
    return video_files

def display_video_list(video_files):
    """Display list of available videos."""
    if not video_files:
        print("\nNo video files found in the videos folder!")
        print("Supported formats: MP4, MOV, AVI, MKV, WMV, FLV, WEBM")
        return False
    
    print("\nAvailable videos:")
    print("-" * 50)
    for idx, video in enumerate(video_files, 1):
        print(f"{idx}. {video}")
    print("-" * 50)
    return True

def get_user_selection(video_files):
    """Get user's video selection."""
    while True:
        try:
            choice = input("\nEnter the number of the video you want to convert (or 'q' to quit): ")
            
            if choice.lower() == 'q':
                return None
            
            choice = int(choice)
            if 1 <= choice <= len(video_files):
                return video_files[choice - 1]
            else:
                print(f"Please enter a number between 1 and {len(video_files)}")
        except ValueError:
            print("Please enter a valid number or 'q' to quit")

def convert_video_to_wav(video_path, output_path):
    """Convert a video file to WAV format."""
    try:
        # Load the video file
        video = VideoFileClip(video_path)
        
        # Check if video has audio track
        if video.audio is None:
            logging.error(f"No audio track found in {video_path}")
            video.close()
            return False
        
        # Extract the audio
        audio = video.audio
        
        # Write the audio to WAV file
        audio.write_audiofile(output_path, 
                            fps=44100,  # Standard audio sample rate
                            nbytes=2,   # 16-bit audio
                            codec='pcm_s16le')  # Standard WAV codec
        
        # Close the video and audio objects
        audio.close()
        video.close()
        
        logging.info(f"Successfully converted {video_path} to {output_path}")
        return True
    except Exception as e:
        logging.error(f"Error converting {video_path}: {str(e)}")
        # Ensure video is closed even if there's an error
        try:
            if 'video' in locals():
                video.close()
        except:
            pass
        return False

def main():
    """Main function to run the video converter."""
    create_directories()
    
    while True:
        # Get and display available videos
        video_files = get_video_files()
        if not display_video_list(video_files):
            break
        
        # Get user selection
        selected_video = get_user_selection(video_files)
        if selected_video is None:
            break
        
        # Convert selected video
        input_path = os.path.join('videos', selected_video)
        output_filename = os.path.splitext(selected_video)[0] + '.wav'
        output_path = os.path.join('video_audios', output_filename)
        
        print(f"\nConverting {selected_video}...")
        if convert_video_to_wav(input_path, output_path):
            print(f"\nConversion successful! Audio saved as: {output_filename}")
        else:
            print("\nConversion failed. Please check the error messages above.")
        
        # Ask if user wants to convert another video
        if input("\nDo you want to convert another video? (y/n): ").lower() != 'y':
            break
    
    print("\nThank you for using the Video to WAV Converter!")

if __name__ == "__main__":
    main() 