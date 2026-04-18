import pandas as pd
from rich.console import Console
from pathlib import Path
from rich.table import Table

def fmt(value) -> str:
    if abs(value) >= 1000:
        return f"{value:.2f}"
    return f"{value:.4f}"


def inspect() -> None:

    console = Console()
    
    ROOT = Path(__file__).resolve().parents[2]
    raw_path = ROOT / "data" / "raw" / "sem_2025_eu.csv"
    features_path = ROOT / "data" / "processed" / "track_features.csv"

    df = pd.read_csv(raw_path)
    tf = pd.read_csv(features_path)

    table = Table(title="HAM CSV Ozeti")

    table.add_column("Sutun")
    table.add_column("Min")
    table.add_column("Max")
    table.add_column("Mean")
    table.add_column("Std")
    table.add_column("NaN")
    table.add_column("Count")

    table_track = Table(title="YAPILANDIRILIŞ CSV Ozeti")

    table_track.add_column("Sutun")
    table_track.add_column("Min")
    table_track.add_column("Max")
    table_track.add_column("Mean")
    table_track.add_column("Std")
    table_track.add_column("NaN")
    table_track.add_column("Count")

    for col in df.columns:
        if pd.api.types.is_numeric_dtype(df[col]):
            table.add_row(
                col,
                fmt(df[col].min()),
                fmt(df[col].max()),
                fmt(df[col].mean()),
                fmt(df[col].std()),
                str(df[col].isna().sum()),
                str(df[col].count())
            )


    for col in tf.columns:
        if pd.api.types.is_numeric_dtype(tf[col]):
            table_track.add_row(
                col,
                fmt(tf[col].min()),
                fmt(tf[col].max()),
                fmt(tf[col].mean()),
                fmt(tf[col].std()),
                str(tf[col].isna().sum()),
                str(tf[col].count())
            )
    
    console.print(table)
    console.print(table_track)

if __name__ == "__main__":
    inspect()


## Tabloda eldeki iki csv içinde min, max, mean, standart sapma(Std), eksik veri(NaN) ve ne kadar veri olduğu gösteriliyor