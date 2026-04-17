import numpy as np
import pandas as pd
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

# m: kaç metreyi bir nokta olarak kabul etmek istediğimiz.
# Minimum 1 olabilir burada 1320 nin tam böleni olmak zorundaki verilerde kayma yada boş satır sorunu görmeyelim

def read(m) -> dict:
    csv_path = ROOT / "data" / "raw" / "sem_2025_eu.csv"
    df = pd.read_csv(csv_path)

    utmx = df["UTMX"].to_numpy()
    utmy = df["UTMY"].to_numpy()

    segment_count = len(utmx) - 1

    if m <= 0:
        raise ValueError("m pozitif bir tam sayı olmalı")
    
    if segment_count % m != 0:
        raise ValueError(f"Segment length {segment_count} değeri m={m} ile tam bölünmüyor!")


    elevation = df["Elevation (m)"].to_numpy()
    distance = df["Distance from Lap Line (m)"].to_numpy()

    dx = np.diff(utmx)
    dy = np.diff(utmy)
    length = distance[-1]

    seq_length = np.hypot(dx, dy)  # n-1
    seq_heading = np.unwrap(np.arctan2(dy, dx))  # n-1
    seq_heading_change = np.diff(seq_heading)  # n-2
    seq_track_progress = distance[1:] / length  # n-1
    seq_slope = np.diff(elevation) / seq_length  # n-1
    seq_curvature = seq_heading_change / np.convolve(seq_length, [0.5, 0.5], mode="valid")  # n-2

    # n-2 uzunluğundaki curvature/heading_change verilerini segmentleme için n-1'e hizalıyoruz.
    seq_heading_change_aligned = np.insert(seq_heading_change, 0, np.nan)
    seq_curvature_aligned = np.insert(seq_curvature, 0, np.nan)
    seq_abs_curvature = np.abs(seq_curvature_aligned)
    seq_elevation_change = np.diff(elevation)
    seq_elevation_start = elevation[:-1]
    seq_elevation_end = elevation[1:]
    seq_distance_to_finish = length - distance[1:]

    seg_curvature = seq_curvature_aligned.reshape(-1, m).mean(axis=1)

    return {
        "seq_x": utmx[1:].reshape(-1, m)[:, -1],
        "seq_y": utmy[1:].reshape(-1, m)[:, -1],
        "seg_length": seq_length.reshape(-1, m).sum(axis=1),
        "seg_heading": seq_heading.reshape(-1, m).mean(axis=1),
        "seg_heading_change": seq_heading_change_aligned.reshape(-1, m).mean(axis=1),
        "seg_track_progress": seq_track_progress.reshape(-1, m)[:, -1],
        "seg_slope": seq_slope.reshape(-1, m).mean(axis=1),
        "seg_curvature": seg_curvature,
        "abs_curvature": seq_abs_curvature.reshape(-1, m).mean(axis=1),
        "curvature_sign": np.sign(seg_curvature),
        "elevation_change": seq_elevation_change.reshape(-1, m).sum(axis=1),
        "elevation_start": seq_elevation_start.reshape(-1, m)[:, 0],
        "elevation_end": seq_elevation_end.reshape(-1, m)[:, -1],
        "distance_to_finish": seq_distance_to_finish.reshape(-1, m)[:, -1],
    }


def create_feature_table() -> None:
    data = read(8)

    output_path = ROOT / "data" / "processed" / "track_features.csv"

    df = pd.DataFrame(
        np.column_stack(list(data.values())),
        columns=data.keys(),
    )

    df["prev_curvature"] = df["seg_curvature"].shift(1)
    df["next_curvature"] = df["seg_curvature"].shift(-1)
    df["prev_slope"] = df["seg_slope"].shift(1)
    df["next_slope"] = df["seg_slope"].shift(-1)

    df.to_csv(output_path, index=False)


if __name__ == "__main__":
    create_feature_table()
