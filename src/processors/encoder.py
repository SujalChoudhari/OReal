import os
import gzip
import io
from PIL import Image

from src.constants import (
    OREAL_FILE_EXT,
    OREAL_DEFAULT_VIDEO_EXT,
    OREAL_MOUSE_EVENT_EXT,
    OREAL_DEFAULT_AUDIO_EXT,
    OREAL_COMPLETE_FILE_HEADER,
    OREAL_DEFAULT_THUMBNAIL_EXT,
)


class Encoder:
    def __init__(self, file_path: str, output_file_path: str = None) -> None:
        """Paths should be without extension"""
        self.avi_file_path = file_path + "." + OREAL_DEFAULT_VIDEO_EXT
        self.audio_file_path = file_path + "." + OREAL_DEFAULT_AUDIO_EXT
        self.mouse_events_file_path = file_path + "." + OREAL_MOUSE_EVENT_EXT
        self.thumbnail_file_path = file_path + "." + OREAL_DEFAULT_THUMBNAIL_EXT

        self.output_directory = os.path.dirname(output_file_path)

        if output_file_path is None:
            self.output_file_path = (
                file_path + ""
                if output_file_path.endswith(OREAL_FILE_EXT)
                else file_path + "." + OREAL_FILE_EXT
            )
        else:
            self.output_file_path = (
                output_file_path + ""
                if output_file_path.endswith(OREAL_FILE_EXT)
                else file_path + "." + OREAL_FILE_EXT
            )

    def encode(self):
        file_sizes = [
            os.path.getsize(self.thumbnail_file_path),
            os.path.getsize(self.avi_file_path),
            os.path.getsize(self.audio_file_path),
            os.path.getsize(self.mouse_events_file_path),
        ]

        with gzip.open(self.output_file_path, "wb") as f_out:
            # Write the sizes of each file to the gzip file header
            for size in file_sizes:
                f_out.write(size.to_bytes(4, byteorder="big"))

            # Write the content of each file to the gzip file
            with open(self.thumbnail_file_path, "rb") as f_in:
                f_out.write(f_in.read())

            with open(self.avi_file_path, "rb") as f_in:
                f_out.write(f_in.read())

            with open(self.audio_file_path, "rb") as f_in:
                f_out.write(f_in.read())

            with open(self.mouse_events_file_path, "rb") as f_in:
                f_out.write(f_in.read())

    def decode(self):
        with gzip.open(self.output_file_path, "rb") as f_in:
            # Read the sizes of each file from the gzip file header
            thumbnail_size = int.from_bytes(f_in.read(4), byteorder="big")
            avi_size = int.from_bytes(f_in.read(4), byteorder="big")
            audio_size = int.from_bytes(f_in.read(4), byteorder="big")
            mouse_events_size = int.from_bytes(f_in.read(4), byteorder="big")

            # Read and write each file's content separately
            with open(self.thumbnail_file_path, "wb") as f_out:
                f_out.write(f_in.read(thumbnail_size))
            with open(self.avi_file_path, "wb") as f_out:
                f_out.write(f_in.read(avi_size))

            with open(self.audio_file_path, "wb") as f_out:
                f_out.write(f_in.read(audio_size))

            with open(self.mouse_events_file_path, "wb") as f_out:
                f_out.write(f_in.read(mouse_events_size))

    def get_thumbnail(self) -> Image:
        with gzip.open(self.output_file_path, "rb") as f_in:
            # Skip the sizes of other files
            thumbnail_size = int.from_bytes(f_in.read(4), byteorder="big")
            f_in.read(4)
            f_in.read(4)
            f_in.read(4)

            # Read the size of the thumbnail

            # Read and return the thumbnail image
            thumbnail_data = f_in.read(thumbnail_size)
            return Image.open(io.BytesIO(thumbnail_data))

