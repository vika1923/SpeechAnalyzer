import numpy as np
from scipy.io import wavfile

def get_rms_per_segment(audio_location, segment_duration_sec=2):
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
        timestamp = i * segment_duration_sec
        results.append((timestamp, rms.item()))

    return results

# path = "video_audios/volumecheck.wav"
# segments = get_rms_per_segment(audio_location=path, segment_duration_sec=3)

# print(*segments, sep="\n")
