import math
import os
from concurrent.futures import ProcessPoolExecutor
from dataclasses import dataclass
from pathlib import Path

import cv2
import numpy as np


@dataclass
class ThumbnailConfig:
    cells: int
    cell_columns: int
    cell_max_width: int
    cell_max_height: int
    cell_border: int


def create_thumbnails(dir_path: Path, config: ThumbnailConfig) -> None:
    video_files = []
    for root, _dirs, files in os.walk(dir_path):
        for file in files:
            if is_video_file(file):
                video_files.append(Path(root) / file)

    with ProcessPoolExecutor() as executor:
        executor.map(create_thumbnail, video_files, [config] * len(video_files))


VIDEO_FILE_EXTENSIONS: set[str] = {
    "3g2",
    "3gp",
    "3gp2",
    "3gpp",
    "amr",
    "amv",
    "asf",
    "avi",
    "bdmv",
    "bik",
    "d2v",
    "divx",
    "drc",
    "dsa",
    "dsm",
    "dss",
    "dsv",
    "evo",
    "f4v",
    "flc",
    "fli",
    "flic",
    "flv",
    "hdmov",
    "ifo",
    "ivf",
    "m1v",
    "m2p",
    "m2t",
    "m2ts",
    "m2v",
    "m4v",
    "mkv",
    "mp2v",
    "mp4",
    "mp4v",
    "mpe",
    "mpeg",
    "mpg",
    "mpls",
    "mpv2",
    "mpv4",
    "mov",
    "mts",
    "ogm",
    "ogv",
    "pss",
    "pva",
    "qt",
    "ram",
    "ratdvd",
    "rm",
    "rmm",
    "rmvb",
    "roq",
    "rpm",
    "smil",
    "smk",
    "swf",
    "tp",
    "tpr",
    "ts",
    "vob",
    "vp6",
    "webm",
    "wm",
    "wmp",
    "wmv",
}


def is_video_file(path: str | Path) -> bool:
    ext = os.path.splitext(path)[1]
    return ext and ext[1:].lower() in VIDEO_FILE_EXTENSIONS


def calc_cell_size(width: int, height: int, max_width: int, max_height: int) -> tuple[int, int]:
    aspect_ratio = width / height
    if aspect_ratio > 1:
        new_height = max_height
        new_width = int(new_height * aspect_ratio)
    else:
        new_width = max_width
        new_height = int(new_width / aspect_ratio)
    return new_width, new_height


def create_thumbnail(path: Path, config: ThumbnailConfig) -> None:
    # 检查文件是否为视频
    if not is_video_file(path):
        raise ValueError(f"{path} is not a video file")

    # 打开视频文件
    capture = cv2.VideoCapture(str(path))
    if not capture.isOpened():
        raise ValueError(f"cannot open {path}")

    # 获取视频信息
    frame_width = int(capture.get(cv2.CAP_PROP_FRAME_WIDTH))
    frame_height = int(capture.get(cv2.CAP_PROP_FRAME_HEIGHT))
    frame_count = int(capture.get(cv2.CAP_PROP_FRAME_COUNT))

    # 计算单元格大小和行数
    cell_width, cell_height = calc_cell_size(frame_width, frame_height, config.cell_max_width, config.cell_max_height)
    cell_rows = int(math.ceil(config.cells / config.cell_columns))

    # 创建结果图像
    result_width = (cell_width + config.cell_border) * config.cell_columns + config.cell_border
    result_height = (cell_height + config.cell_border) * cell_rows + config.cell_border
    result_image = np.full((result_height, result_width, 3), 255, dtype=np.uint8)

    # 生成缩略图
    for cell_index, frame_index in enumerate(np.linspace(0, frame_count, config.cells, endpoint=False, dtype=int)):
        capture.set(cv2.CAP_PROP_POS_FRAMES, float(frame_index))
        success, frame = capture.read()
        if not success:
            raise ValueError(f"cannot read frame {frame_index} from {path}")

        cell_x, cell_y = cell_index % config.cell_columns, cell_index // config.cell_columns
        result_x, result_y = (
            cell_x * (cell_width + config.cell_border) + config.cell_border,
            cell_y * (cell_height + config.cell_border) + config.cell_border,
        )
        result_image[result_y : result_y + cell_height, result_x : result_x + cell_width] = cv2.resize(
            frame,
            (cell_width, cell_height),
            interpolation=(cv2.INTER_AREA if cell_height < frame_height else cv2.INTER_CUBIC),
        )

    # 保存缩略图
    result_image_path = path.with_suffix(".jpg")
    cv2.imwrite(str(result_image_path), result_image)
    print(f"OK: {result_image_path}")
