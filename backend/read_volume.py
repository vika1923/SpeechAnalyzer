import numpy as np
from scipy.io import wavfile
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    filename='api_server.log',
    filemode='a'
)
logger = logging.getLogger(__name__)

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

        first_sample = None

        for i in range(num_segments):
            start = i * segment_samples
            end = start + segment_samples
            segment = data[start:end]
            rms = np.sqrt(np.mean(segment**2))
            if i == 0:
                first_sample = rms.item() if rms.item() != 0 else 1e-8  # avoid division by zero
            timestamp = i * segment_duration_sec
            normalized_rms = rms.item() / first_sample if first_sample else 0.0
            results.append((timestamp, normalized_rms))
        
        # print("RESULTS FROM READVOLUMEPY:", results)
        logger.info(f"Successfully calculated RMS for {audio_location}")
        return results
    except Exception as e:
        logger.error(f"Error in get_rms_per_segment for {audio_location}: {e}", exc_info=True)
        raise

# path = "video_audios/scream.wav"
# segments = get_rms_per_segment(audio_location=path, segment_duration_sec=3)

# print(*segments, sep="\n")
