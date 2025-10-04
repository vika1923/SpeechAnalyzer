import numpy as np
from scipy.io import wavfile
from my_logger import get_logger

logger = get_logger(__name__)

def get_rms_per_segment(audio_location: str, segment_duration_sec: float=2):
    logger.info(f"get_rms_per_segment called for {audio_location}")
    try:
        sample_rate, data = wavfile.read(audio_location)

        # Convert to mono if stereo
        if len(data.shape) == 2:
            data = data.mean(axis=1)

        total_samples = len(data)
        segment_samples = int(segment_duration_sec * sample_rate)
        num_segments = total_samples // segment_samples

        results = []

        for i in range(num_segments):
            start = i * segment_samples
            end = start + segment_samples
            segment = data[start:end]
            rms = np.sqrt(np.mean(segment**2))
            # Avoid log(0) by setting a minimum value
            if rms == 0:
                db = -np.inf
            else:
                db = 20 * np.log10(rms)
            timestamp = i * segment_duration_sec
            results.append((timestamp, db))
        
        logger.info(f"Successfully calculated dB for {audio_location}")
        return results
    except Exception as e:
        logger.error(f"Error in get_rms_per_segment for {audio_location}: {e}", exc_info=True)
        raise

def assign_volume_points(volume:float):
    if volume < 30:
        return 0
    elif volume < 37:
        return 1
    elif volume < 43:
        return 2
    elif volume < 48:
        return 3
    elif volume < 53:
        return 4
    elif volume < 58:
        return 5
    elif volume < 64:
        return 6
    elif volume < 70:
        return 7
    elif volume < 78:
        return 8
    elif volume < 85:
        return 9
    else:
        return 10
# path = "video_audios/scream.wav"
# segments = get_rms_per_segment(audio_location=path, segment_duration_sec=3)

# print(*segments, sep="\n")
