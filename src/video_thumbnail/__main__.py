import argparse
from pathlib import Path

import rich.traceback

from video_thumbnail import ThumbnailConfig, create_thumbnail, create_thumbnails


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="生成视频缩略图", formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    parser.add_argument("path", type=Path, help="视频路径")
    parser.add_argument("--cells", "-c", type=int, default=16, help="缩略图数量")
    parser.add_argument("--cell-columns", "-s", type=int, default=4, help="每行多少个缩略图")
    parser.add_argument("--cell-max-width", "-w", type=int, default=720, help="缩略图最大宽度")
    parser.add_argument("--cell-max-height", "-t", type=int, default=720, help="缩略图最大高度")
    parser.add_argument("--cell-border", "-b", type=int, default=20, help="缩略图边框")
    return parser.parse_args()


def check_params(
    path: Path, cells: int, cell_columns: int, cell_max_width: int, cell_max_height: int, cell_border: int
) -> None:
    if not path.exists():
        raise FileNotFoundError(f"{path} does not exist")
    if cells < 1:
        raise ValueError(f"{cells} is less than 1")
    if cell_columns < 1:
        raise ValueError(f"{cell_columns} is less than 1")
    if cell_max_width < 1:
        raise ValueError(f"{cell_max_width} is less than 1")
    if cell_max_height < 1:
        raise ValueError(f"{cell_max_height} is less than 1")
    if cell_border < 0:
        raise ValueError(f"{cell_border} is less than 0")


def main(
    path: Path, cells: int, cell_columns: int, cell_max_width: int, cell_max_height: int, cell_border: int
) -> None:
    check_params(path, cells, cell_columns, cell_max_width, cell_max_height, cell_border)
    config = ThumbnailConfig(
        cells=cells,
        cell_columns=cell_columns,
        cell_max_width=cell_max_width,
        cell_max_height=cell_max_height,
        cell_border=cell_border,
    )
    if path.is_file():
        create_thumbnail(path, config)
    elif path.is_dir():
        create_thumbnails(path, config)
    else:
        raise ValueError(f"{path} is neither a file nor a directory")


if __name__ == "__main__":
    rich.traceback.install(show_locals=True)
    args = parse_args()
    main(args.path, args.cells, args.cell_columns, args.cell_max_width, args.cell_max_height, args.cell_border)
