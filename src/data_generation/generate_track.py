import pandas as pd
import numpy as np
from pathlib import Path
import random
from math import atan2, hypot

def can_return(
    new_heading: float,
    new_remaining_step: int,
    base_x: float,
    base_y: float,
    new_x: float,
    new_y: float,
    max_heading_change: float,
) -> bool:

    required_lenght = hypot(base_y - new_y, base_x - new_x)
    required_heading = atan2(base_y - new_y, base_x - new_x)

    heading_error = required_heading - new_heading

    while heading_error > np.pi:
        heading_error -= 2 * np.pi
    while heading_error < -np.pi:
        heading_error += 2 * np.pi

    max_possible_turn = new_remaining_step * max_heading_change

    if required_lenght > new_remaining_step:
        return False

    if abs(heading_error) > max_possible_turn:
        return False

    return True

def generate_heading_change(
        remaining_step : int, 
        cur_x : float, 
        cur_y : float, 
        base_x : float, 
        base_y : float, 
        curr_heading : float
    ) -> list:
    
    max_heading_change = 0.02
    min_heading_change = 0.001

    try_ = [0, 1, 2]

    while True:
        
        return_vector_degree = atan2(base_y - cur_y, base_x - cur_x)
        
        if remaining_step > 100:
        
            duration = random.randint(1, min(15, remaining_step))

            if try_:
                way = random.choice(try_)
            else:
                duration = min(remaining_step, 5)
                heading_error = return_vector_degree - curr_heading
                heading_change = max(-max_heading_change, min(max_heading_change, heading_error))
                break



            if way == 0:
                heading_change = 0.0
            elif way == 1:
                heading_change = random.uniform(min_heading_change, max_heading_change)
            else:
                heading_change = -random.uniform(min_heading_change, max_heading_change)

            temp_heading = curr_heading
            temp_x = cur_x
            temp_y = cur_y

            for _ in range(duration):
                temp_heading += heading_change
                temp_x += np.cos(temp_heading)
                temp_y += np.sin(temp_heading)

            new_x = temp_x
            new_y = temp_y
            new_remaining_step = remaining_step - duration

            if can_return(temp_heading, new_remaining_step, base_x, base_y, new_x, new_y, max_heading_change):
                break

            try_.remove(way)
            continue


        else:
            duration = remaining_step
            heading_error = return_vector_degree - curr_heading

            while heading_error > np.pi:
                heading_error -= 2 * np.pi
            while heading_error < -np.pi:
                heading_error += 2 * np.pi

            heading_change = max(-max_heading_change, min(max_heading_change, heading_error))

            break

    return [heading_change] * duration
def x_y(distance : np.ndarray) -> tuple:

    x = np.array([0.0])
    y = np.array([0.0])

    heading = 0.0

    remaining = len(distance) - 1

    while remaining != 0:

        read_heading_change = generate_heading_change(remaining, x[-1], y[-1], x[0], y[0], heading)

        temp_remaining = remaining
        temp_heading = heading

        temp_x = x[-1]
        temp_y = y[-1]

        temp_x_list = np.copy(x)
        temp_y_list = np.copy(y)

        block_succes = True

        for i in range(len(read_heading_change)):
            temp_heading += read_heading_change[i]
            temp_x += np.cos(temp_heading) 
            temp_y += np.sin(temp_heading)
            temp_remaining -= 1

            # valla burayı ai yaptı kafam basmadı
            point_exists = np.any(
                (np.abs(temp_x_list - temp_x) < 1e-6) &
                (np.abs(temp_y_list - temp_y) < 1e-6)
            )

            if point_exists:
                block_succes = False
                break
            else:
                temp_x_list = np.append(temp_x_list, temp_x)
                temp_y_list = np.append(temp_y_list, temp_y)


        if block_succes:
            remaining = temp_remaining
            x = temp_x_list
            y = temp_y_list
            heading = temp_heading

    return x, y


def main(length : int, out_path) -> None:

    distance = np.arange(0, length, 1)

    elevation = np.linspace(200, 202, length)

    utmx, utmy = x_y(distance)
    
    df = pd.DataFrame({"Distance from Lap Line (m)" : distance, "Elevation (m)" : elevation, "UTMX" : utmx, "UTMY" : utmy})

    df.to_csv(out_path, index=False)



if __name__ == "__main__":

    ROOT = Path(__file__).resolve().parents[2]

    path = ROOT / "data" / "generated" / "GeneratedTrack.csv"
    
    main(1000, path)
