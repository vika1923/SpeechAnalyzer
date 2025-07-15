import subprocess 
import polars as pl
import logging

def extract_video(file_path, out_dir, file_name = "video", openface_path='/opt/OpenFace/build/bin/FeatureExtraction'): 
    subprocess.run([
        openface_path,  # Use absolute path
        '-f', file_path,
        '-out_dir', out_dir,
        '-of', file_name, 
        '-gaze',
        '-aus'
    ])

def get_gaze_and_aus(file_path):
    gaze = ["gaze_angle_x", "gaze_angle_y"]
    aus = [
        "AU01_r", "AU02_r", "AU04_r", "AU05_r", "AU06_r", "AU07_r",
        "AU09_r", "AU10_r", "AU12_r", "AU14_r", "AU15_r", "AU17_r",
        "AU20_r", "AU23_r", "AU25_r", "AU26_r", "AU45_r",
    ]
    print("Yes")
    df = pl.read_csv(file_path, columns=gaze + aus)

    result = {}

    # Sum of absolute gaze angles
    gaze_sums = df.select([pl.col(col).abs().mean().alias(col + "_abs_sum") for col in gaze])
    result.update(dict(zip(gaze, gaze_sums.row(0))))

    # Sum of absolute diffs for AUs
    for col in aus:
        diff_sum = df.select(
            (pl.col(col) - pl.col(col).shift(1)).abs().mean().alias(col + "_diff_sum")
        )[0, 0]
        result[col] = diff_sum

    return result

def get_all_aus_sum(dick):
    sum = 0
    for key, value in dick.items():
        if "AU" in key:
            sum += value
    return sum

def return_numbers(file_path, openface_path='/opt/OpenFace/build/bin/FeatureExtraction', temp_dir = "app/videos/openface"):
    logging.basicConfig(level=logging.INFO)
    try:
        # temp_dir = "/app/videos/openface"  # Use absolute path that exists in container
        extract_video(file_path, temp_dir, openface_path=openface_path)
        print("No")
        out = get_gaze_and_aus(temp_dir+"/video.csv") # add stuff
        result = (out['gaze_angle_x'], out['gaze_angle_y'], get_all_aus_sum(out))
        logging.info(f"return_numbers({file_path}) returns: {result}")
    except Exception as e:
        logging.error(f"return_numbers({file_path}) failed: {e}")
        return (None, None, None)
    return result

if __name__ == "__main__":
    print("Hello")
    numbers = return_numbers('/Users/almaz/PycharmProjects/SpeechAnalyzer/videos/Vika.mov', 
                             '/Users/almaz/PycharmProjects/SpeechAnalyzer/openFace/OpenFace/build/bin/FeatureExtraction', 
                             '/Users/almaz/PycharmProjects/SpeechAnalyzer/videos/tests')
