import math

import cv2
import numpy as np
from rich.traceback import install

video_path = r"./frame_index_video.mp4"
cell_size = 16
cell_column_count = 4
cell_max_size = (720, 720)
cell_border = 20

install(show_locals=True)


def calc_resized_size(width: int, height: int, max_width: int, max_height: int) -> tuple[int, int]:
    aspect_ratio = width / height
    if aspect_ratio > 1:
        new_height = max_height
        new_width = int(new_height * aspect_ratio)
    else:
        new_width = max_width
        new_height = int(new_width / aspect_ratio)
    return new_width, new_height


capture = cv2.VideoCapture(video_path)
if not capture.isOpened():
    raise RuntimeError(f"cannot open {video_path}")

image_props = {}
for attr_name in dir(cv2):
    if attr_name.startswith("CAP_PROP_"):
        attr = getattr(cv2, attr_name)
        attr_value = capture.get(attr)
        if attr_value != 0:
            image_props[attr_name] = attr_value
print(image_props)

frame_width = capture.get(cv2.CAP_PROP_FRAME_WIDTH)
frame_height = capture.get(cv2.CAP_PROP_FRAME_HEIGHT)
frame_count = capture.get(cv2.CAP_PROP_FRAME_COUNT)

cell_width, cell_height = calc_resized_size(frame_width, frame_height, *cell_max_size)
cell_row_count = int(math.ceil(cell_size / cell_column_count))
result_width = (cell_width + cell_border) * cell_column_count + cell_border
result_height = (cell_height + cell_border) * cell_row_count + cell_border
result_image = np.full((result_height, result_width, 3), 255, dtype=np.uint8)
for i, frame_index in enumerate(np.linspace(0, frame_count - 1, cell_size, dtype=int)):
    capture.set(cv2.CAP_PROP_POS_FRAMES, frame_index)
    _, frame = capture.read()
    frame = cv2.resize(
        frame,
        (cell_width, cell_height),
        interpolation=(cv2.INTER_AREA if cell_height < frame_height else cv2.INTER_CUBIC),
    )

    cell_x, cell_y = i % cell_column_count, i // cell_column_count
    result_x, result_y = (
        cell_x * (cell_width + cell_border) + cell_border,
        cell_y * (cell_height + cell_border) + cell_border,
    )
    result_image[result_y : result_y + cell_height, result_x : result_x + cell_width] = frame

cv2.imwrite("result.jpg", result_image)
