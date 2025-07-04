import subprocess 
import polars as pl
import os

def extract_video(file_path, out_dir, file_name = "video"): 
    subprocess.run([
        '.\openFace\OpenFace\FeatureExtraction.exe', # CHANGED FOR WINDOWS 
        '-f', file_path,
        '-out_dir', out_dir,
        '-of', file_name, 
        '-gaze',
        '-aus'
    ])
def get_gaze_and_aus(file_path):
    gaze = [" gaze_angle_x", " gaze_angle_y"]
    gaze_vecs = [
        " gaze_0_x", " gaze_0_y", " gaze_0_z",
        " gaze_1_x", " gaze_1_y", " gaze_1_z"
    ]
    aus = [
        " AU01_r", " AU02_r", " AU04_r", " AU05_r", " AU06_r", " AU07_r",
        " AU09_r", " AU10_r", " AU12_r", " AU14_r", " AU15_r", " AU17_r",
        " AU20_r", " AU23_r", " AU25_r", " AU26_r", " AU45_r",
    ]
    all_columns = gaze + gaze_vecs + aus
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"CSV file not found: {file_path}")
    try:
        df = pl.read_csv(file_path, columns=all_columns)
    except Exception as e:
        raise RuntimeError(f"Error reading CSV file {file_path}: {e}")
    # Ensure all columns are float to avoid abs() errors on strings
    for col in all_columns:
        if col not in df.columns:
            raise KeyError(f"Column '{col}' not found in CSV file {file_path}. Columns found: {df.columns}")
        df = df.with_columns(
            pl.col(col).str.strip_chars().cast(pl.Float64)
        )

    result = {}

    # Gaze Angles
    try:
        gaze_sums = df.select([pl.col(col).abs().mean().alias(col + "_abs_sum") for col in gaze])
        result.update(dict(zip(gaze, gaze_sums.row(0))))
    except Exception as e:
        raise RuntimeError(f"Error calculating gaze sums: {e}")

    # Gaze Vectors (mean for each component)
    for col in gaze_vecs:
        try:
            result[col] = df[col].mean()
        except Exception as e:
            raise RuntimeError(f"Error calculating mean for gaze vector {col}: {e}")

    # Sum of absolute diffs for AUs
    for col in aus:
        try:
            diff_sum = df.select(
                (pl.col(col) - pl.col(col).shift(1)).abs().mean().alias(col + "_diff_sum")
            )[0, 0]
            result[col] = diff_sum
        except Exception as e:
            raise RuntimeError(f"Error calculating AU diff sum for {col}: {e}")

    return result

def get_all_aus_sum(dick):
    sum = 0
    for key, value in dick.items():
        if "AU" in key:
            sum += value
    return sum

def return_numbers(file_path):
    temp_dir = "videos/openface"
    extract_video(file_path, temp_dir)
    out = get_gaze_and_aus(temp_dir+"/video.csv")
    # Check for required keys
    for key in [" gaze_angle_x", " gaze_angle_y"]:
        if key not in out:
            raise KeyError(f"Key '{key}' not found in output from get_gaze_and_aus. Keys found: {list(out.keys())}")
    # Gather gaze vectors
    gaze_vecs = [
        " gaze_0_x", " gaze_0_y", " gaze_0_z",
        " gaze_1_x", " gaze_1_y", " gaze_1_z"
    ]
    gaze_vector_values = {k: out[k] for k in gaze_vecs}
    # Gather all AU values
    aus = [
        " AU01_r", " AU02_r", " AU04_r", " AU05_r", " AU06_r", " AU07_r",
        " AU09_r", " AU10_r", " AU12_r", " AU14_r", " AU15_r", " AU17_r",
        " AU20_r", " AU23_r", " AU25_r", " AU26_r", " AU45_r",
    ]
    au_values = {k: out[k] for k in aus}
    return {
        'gaze_angle_x': out[' gaze_angle_x'],
        'gaze_angle_y': out[' gaze_angle_y'],
        'gaze_vectors': gaze_vector_values,
        'aus': au_values,
        'all_aus_sum': get_all_aus_sum(out)
    }


if __name__ == "__main__":
    extract_video('videos/vika2.mp4', 'videos')