import numpy as np
from scipy.io import wavfile

def get_rms_per_segment(audio_location: str, segment_duration_sec: float=2):
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

    return results

# path = "video_audios/scream.wav"
# segments = get_rms_per_segment(audio_location=path, segment_duration_sec=3)

# print(*segments, sep="\n")
