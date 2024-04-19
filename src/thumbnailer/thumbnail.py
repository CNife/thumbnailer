import math
from dataclasses import dataclass
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


@dataclass
class ThumbnailConfig:
    cells: int
    cell_columns: int
    cell_max_width: int
    cell_max_height: int
    cell_border: int


@dataclass
class FontConfig:
    name: str
    variant: str
    size: int


FONT = None
_font_dir = Path(__file__).parent.parent.parent / "fonts"
FONTS_CONFIG: dict[str, Path] = {"SourceHanSanSC": _font_dir / "SourceHanSansSC-VF.otf"}


def init_font(config: FontConfig) -> None:
    global FONT
    if config.name not in FONTS_CONFIG:
        raise ValueError(f"font {config.name} is not found")
    font_path = FONTS_CONFIG[config.name]
    FONT = ImageFont.truetype(str(font_path), config.size)
    if config.variant not in FONT.get_variation_names():
        raise ValueError(f"font {config.name} does not have variant {config.variant}")
    FONT.set_variation_by_name(config.variant)


def get_font() -> ImageFont:
    assert FONT is not None
    return FONT


def calc_cell_size(width: int, height: int, max_width: int, max_height: int) -> tuple[int, int]:
    aspect_ratio = width / height
    if aspect_ratio > 1:
        new_height = max_height
        new_width = int(new_height * aspect_ratio)
    else:
        new_width = max_width
        new_height = int(new_width / aspect_ratio)
    return new_width, new_height


class Thumbnail:
    def __init__(
        self, title: str, cells: int, cell_columns: int, cell_width: int, cell_height: int, border: int
    ) -> None:
        self.title = title
        self.cells = cells
        self.cell_columns = cell_columns
        self.cell_width = cell_width
        self.cell_height = cell_height
        self.border = border

        self._make_image()
        self._write_title()

        self.current_cell = 0

    def _make_image(self):
        _, top, _, bottom = get_font().getbbox(self.title)
        self.title_height = bottom - top
        self.cell_rows = int(math.ceil(self.cells / self.cell_columns))
        image_height = self.border + self.title_height + (self.border + self.cell_height) * self.cell_rows
        image_width = self.border + (self.cell_width + self.border) * self.cell_columns
        self.image = Image.new("RGB", (image_width, image_height), (255, 255, 255))

    def _write_title(self) -> None:
        font = get_font()
        draw = ImageDraw.Draw(self.image)
        draw.text((self.border, self.border), self.title, font=font, fill=(0, 0, 0))

    def add_cell(self, image: Image) -> None:
        if self.current_cell >= self.cells:
            raise ValueError("too many cells")
        self.current_cell += 1

        if self.image.size != (self.cell_width, self.cell_height):
            image = image.resize((self.cell_width, self.cell_height))

        cell_row = self.current_cell // self.cell_columns
        cell_column = self.current_cell % self.cell_columns
        left = self.border + (self.cell_width + self.border) * cell_column
        top = self.border * 2 + self.title_height + (self.border + self.cell_height) * cell_row
        self.image.paste(image, (left, top))

    def save(self, path: Path) -> None:
        self.image.save(path)
