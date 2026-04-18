import numpy as np
import pandas as pd
from pathlib import Path
from rich.console import Console

# Amacı eldeki pistin doğruluğu yerine ileride eğitim için oluşturulacak yapay pistlerin doğrulunu test etmek.


def check_required_columns(df) -> list:
    
    required = ["Distance from Lap Line (m)", "Elevation (m)", "UTMX", "UTMY"]
    missing = []

    for req in required:
        if req not in df.columns:
            missing.append(req)
    
    return missing

def check_missing_values(df) -> dict:
    
    nan_dict = {}

    for col in df.columns:
        nan_count = df[col].isna().sum()

        if nan_count > 0:
            nan_rows = df[df[col].isna()].index

            nan_dict[df[col].name] = [nan_count, nan_rows.tolist()]
    
    return nan_dict

def check_distance_consistency(df, tolerance : float) -> dict:

    problem_dict = {}

    diff = np.diff(df["Distance from Lap Line (m)"].to_numpy())

    mean = np.mean(diff)

    less_than_zero = np.where(diff < 0)[0]

    if less_than_zero.size != 0:
        problem_dict["Uzaklığın negatif yönde değiştiği satırlar"] = less_than_zero
    
    zero_step_rows = np.where(diff == 0)[0]

    if zero_step_rows.size != 0:
        problem_dict["Uzaklığın değişmediği satırlar"] = zero_step_rows

    distance_outlier_rows = np.where((diff < (mean - mean*tolerance) ) | (diff > (mean + mean*tolerance)))[0]

    if distance_outlier_rows.size != 0:
        problem_dict["Uzaklığın ortalamaya göre çok değiştiği satırlar"] = distance_outlier_rows
    
    return problem_dict

def check_geometry(df, tolerance_mean : float, tolerance_diff : float) -> dict:
    
    utmx = df["UTMX"].to_numpy()
    utmy = df["UTMY"].to_numpy()

    dx = np.diff(utmx)
    dy = np.diff(utmy)

    step_length = np.hypot(dx, dy)

    problem_dict = {}

    mean = np.mean(step_length)
    
    zero_step_rows = np.where(step_length == 0)[0]

    if zero_step_rows.size != 0:
        problem_dict["Uzaklığın geometrik olarak değişmediği satırlar"] = zero_step_rows

    distance_outlier_rows = np.where((step_length < (mean - mean*tolerance_mean) ) | (step_length > (mean + mean*tolerance_mean)))[0]

    if distance_outlier_rows.size != 0:
        problem_dict["Uzaklığın geometrik olarak ortalamaya göre çok değiştiği satırlar"] = distance_outlier_rows
    
    distance_diff  = np.diff(df["Distance from Lap Line (m)"].to_numpy())

    problem_lines = []

    for i in range(distance_diff.size):
        if abs(distance_diff[i] - step_length[i]) > tolerance_diff:
            problem_lines.append(i)

    if problem_lines:
        problem_dict["Ham ve geometrik uzaklığın uyuşmadığı satırlar"] = problem_lines

    return problem_dict


    
def validate_raw(raw_track_data: str | Path) -> None:

    df = pd.read_csv(raw_track_data)

    console = Console()

    missing_columns = check_required_columns(df)

    if missing_columns:
        raise ValueError(f"Veride eksik sütun var {missing_columns}")
    else:
        console.print(
            "[bold green]Veride eksik sütun yok.",
            )

    console.print("\n[bold cyan]==============================================\n")

    total_problems = 0

    nan_dict = check_missing_values(df)

    if nan_dict:

        for key in nan_dict:
            console.print(
                f"[bold red]Sütun : {key}",
                f"[bold red]NaN sayısı : {nan_dict.get(key)[0]}",
                f"[bold red]Satır : {nan_dict.get(key)[1]}"
                )
            
            total_problems += 1
    else:
        console.print(
            "[bold green]Sütunlarda eksik veri yok.",
            )

    console.print("\n[bold cyan]==============================================\n")

    problem_dict = check_distance_consistency(df, 0.2)

    if problem_dict:
        
        for key in problem_dict:
            console.print(
                f"[bold red]{key} : {problem_dict.get(key)}"
            )

            total_problems += 1
    else:
        console.print(
            "[bold green]Distance sütununda anormal bir veri yok.",
            )
        
    console.print("\n[bold cyan]==============================================\n")

    problem_dict = check_geometry(df, 0.2, 0.1)

    if problem_dict:
        
        for key in problem_dict:
            console.print(
                f"[bold red]{key} : {problem_dict.get(key)}"
            )

            total_problems += 1
    else:
        console.print(
            "[bold green]Geometrik adım uzunluklarında anormal bir veri yok.",
            )

    console.print("\n[bold cyan]==============================================\n")


    total_lines = len(df)

    if total_problems > 0.3 * total_lines:
        console.print(
            "[bold red]---FAIL--- ",
            f"\n[bold red]Total : {total_problems} exist"
            )
    elif total_problems > 0:
        console.print(
            "[bold yellow]---WARNING--- ",
            f"\n[bold yellow]Total : {total_problems} problem exist"
            )
    else:
        console.print(
            "[bold green]---PASS--- ",
            f"\n[bold green]Ther is no any problem"
            )
    
if __name__ == "__main__":

    ROOT = Path(__file__).resolve().parents[2]
    track_data = ROOT / "data" / "raw" / "sem_2025_eu.csv"


    validate_raw(track_data)