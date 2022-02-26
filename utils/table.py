"""
Contains the `Table` class, to convert an iterable into an image of a table.
"""

from math import ceil

from PIL import ImageFont, Image, ImageDraw, ImageChops
from tabulate import tabulate

MARGIN_PIXELS = 2
IMAGE_PATH = "../.table.png"


class Table:
    """
    Wrapper for a single method (`iter_to_image`), for consistency's sake only.
    """

    @staticmethod
    def data_to_image(headers: list[str], rows: list[list[str]]):
        """
        Converts the passed iterable into an image of a table and saves it in the `.table` file.
        """
        lines = Table._data_to_table(headers, rows)
        Table._table_to_image(lines)

    @staticmethod
    def _data_to_table(headers: list[str], rows: list[list[str]]) -> list[str]:
        """
        Uses the `tabulate` package to create a table using ASCII characters.
        :param headers: List of headers of the table.
        :param rows: Row-wise data in the table.
        :return: ASCII table as a list of lines.
        """
        table_string = tabulate(
            rows,
            headers=headers,
            tablefmt="grid",
        )
        return table_string.splitlines()

    @staticmethod
    def _table_to_image(lines: list[str]) -> None:
        """
        Draws the passed ASCII table using `Pillow` and save to `IMAGE_PATH`.
        :param lines: ASCII table as a list of lines.
        """
        font = ImageFont.truetype(font="font-style.ttf", size=40)

        image, draw, max_line_height = Table._draw_background(lines, font)
        Table._draw_text(draw, lines, font, max_line_height)
        Table._save(image)

    @staticmethod
    def _draw_background(
            lines: list[str],
            font: ImageFont,
    ) -> tuple[Image, ImageDraw, int]:
        # Calculate dimensions
        tallest_line = max(lines, key=lambda line: font.getsize(line)[1])
        widest_line = max(lines, key=lambda line: font.getsize(line)[0])
        max_line_height, max_line_width = (
            Table._fpt_to_px(font.getsize(tallest_line)[1]),
            Table._fpt_to_px(font.getsize(widest_line)[0]),
        )
        image_height = ceil(max_line_height * 0.8 * len(lines) + 2 * MARGIN_PIXELS)
        image_width = ceil(max_line_width + 2 * MARGIN_PIXELS)

        # Draw the background
        background_color = 255
        image = Image.new("L", (image_width, image_height), color=background_color)
        draw = ImageDraw.Draw(image)

        return image, draw, max_line_height

    @staticmethod
    def _draw_text(
            draw: ImageDraw,
            lines: list[str],
            font: ImageFont,
            max_line_height: int,
    ):
        for i, line in enumerate(lines):
            draw.text(
                (MARGIN_PIXELS, round(MARGIN_PIXELS + i * max_line_height * 0.8)),
                line,
                fill=0,
                font=font,
            )

    @staticmethod
    def _fpt_to_px(points: int) -> int:
        """
        Converts font points to pixels
        :param points: Font points value
        :return: Pixels value
        """
        return round(points * 96 / 72)

    @staticmethod
    def _save(image: Image):
        background = image.getpixel((0, 0))
        border = Image.new("L", image.size, background)
        diff = ImageChops.difference(image, border)
        bbox = diff.getbbox()
        image = image.crop(bbox) if bbox else image
        image.save(IMAGE_PATH)
