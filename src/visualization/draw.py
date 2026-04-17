import matplotlib.pyplot as plt
import pandas as pd
from pathlib import Path

def load_data():
    root = Path(__file__).resolve().parents[2]
    raw_path = root / "data" / "raw" / "sem_2025_eu.csv"
    features_path = root / "data" / "processed" / "track_features.csv"

    raw_df = pd.read_csv(raw_path)
    features_df = pd.read_csv(features_path)
    return raw_df, features_df


def draw_2d() -> None:
    df, tf = load_data()

    fig, ax = plt.subplots(3, 1, figsize=(12, 14))

    ax[0].plot(df["UTMX"], df["UTMY"])
    ax[0].set_aspect('equal')
    ax[0].set_title("Pist")

    sc1 = ax[1].scatter(tf["seq_x"], tf["seq_y"], c=abs(tf["seg_curvature"]), cmap="coolwarm", s=3)
    ax[1].set_aspect('equal')
    ax[1].set_title("Curvature")
    
    sc2 = ax[2].scatter(tf["seq_x"], tf["seq_y"], c=tf["seg_slope"], cmap="coolwarm", s=3)
    ax[2].set_aspect("equal")
    ax[2].set_title("Slope")
    
    plt.colorbar(sc2, ax=ax[2], label="Slope")
    plt.colorbar(sc1, ax=ax[1], label="Curvature")
    plt.show()

def draw_3d() -> None:
    
    df, tf = load_data()
    
    fig = plt.figure()
    ax = fig.add_subplot(111, projection="3d")

    z = df["Elevation (m)"]
    ax.plot(df["UTMX"], df["UTMY"], (z - z.min()))
    ax.set_zlim(0, 12)
    plt.show()

if __name__ == "__main__":
    draw_2d()
