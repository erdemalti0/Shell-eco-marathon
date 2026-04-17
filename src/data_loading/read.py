import numpy as np
import pandas as pd
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

# m: kaç metreyi bir nokta olarak kabul etmek istediğimiz.
# Minimum 1 olabilir burada 1320 nin tam böleni olmak zorundaki verilerde kayma yada boş satır sorunu görmeyelim

def read(m) -> dict:

    csv_path = ROOT / "data" / "raw" / "sem_2025_eu.csv"
    df = pd.read_csv(csv_path) #n

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

    seq_length = np.hypot(dx, dy) #n-1
    seq_heading = np.unwrap(np.arctan2(dy, dx)) #n-1
    seq_heading_change = np.diff(seq_heading) #n-2
    seq_track_progress = np.array(distance[1::] / length) #n-1
    seq_slope = np.array(np.diff(elevation) / seq_length) #n-1
    seq_curvature = np.array(seq_heading_change / np.convolve(seq_length, [0.5, 0.5], mode="valid")) #n-2   

    
    return {
        'seq_x':utmx[1:].reshape(-1, m)[:, -1],
        'seq_y':utmy[1:].reshape(-1, m)[:, -1],
        'seg_length':seq_length.reshape(-1, m).sum(axis=1),
        'seg_heading':seq_heading.reshape(-1, m).mean(axis=1),
        'seg_heading_change': np.insert(seq_heading_change, 0, np.nan).reshape(-1, m).mean(axis=1),
        'seg_track_progress': seq_track_progress.reshape(-1, m)[:, -1],
        'seg_slope': seq_slope.reshape(-1, m).mean(axis=1),
        'seg_curvature': np.insert(seq_curvature, 0, np.nan).reshape(-1, m).mean(axis=1)
        #Burda n-2 değerlerinin başına sorun çıkasın diye nan ekliyorum fakat bize sorun çıkarabilecek bir yöntem düzeltirmesi gerek
    }
    

def create_feature_table() -> None:
    data = read(8)

    output_path = ROOT / "data" / "processed" / "track_features.csv"

    df = pd.DataFrame(
        np.column_stack(list(data.values())),
        columns = data.keys()
    )
    
    df.to_csv(output_path, index=False)


if __name__ == "__main__":
    create_feature_table()