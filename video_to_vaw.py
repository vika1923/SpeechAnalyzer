import os
from moviepy.editor import VideoFileClip
import logging
from typing import Optional

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    filename='api_server.log',
    filemode='a'
)
logger = logging.getLogger(__name__)

def convert_video_to_wav(video_path: str) -> Optional[str]:
    """Convert a video file to WAV format and save in video_audios/ folder."""
    logger.info(f"convert_video_to_wav called with video_path: {video_path}")
    os.makedirs('video_audios', exist_ok=True)

    try:
        video = VideoFileClip(video_path)

        if video.audio is None:
            logger.error(f"No audio track found in {video_path}")
            video.close()
            return None
 
        # Generate output path
        filename = os.path.splitext(os.path.basename(video_path))[0] + '.wav'
        output_path = os.path.join('video_audios', filename)

        # Write the audio to a WAV file
        video.audio.write_audiofile(
            output_path,
            fps=44100,
            nbytes=2,
            codec='pcm_s16le'
        )

        video.audio.close()
        video.close()

        logger.info(f"Audio extracted and saved to: {output_path}")
        return output_path

    except Exception as e:
        logger.error(f"Error converting video to WAV: {e}", exc_info=True)
        return None

# convert_video_to_wav(video_path="videos/scream.mp4")