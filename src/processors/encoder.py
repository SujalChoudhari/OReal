import os
import gzip

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
        self.output_directory = os.path.dirname(output_file_path)
        if output_file_path is None:
            self.output_file_path = file_path + "." + OREAL_FILE_EXT
        else:
            self.output_file_path = output_file_path + "." + OREAL_FILE_EXT

    def encode(self):
        file_paths = [
            self.avi_file_path,
            self.audio_file_path,
            self.mouse_events_file_path,
        ]

        with gzip.open(self.output_file_path, "wb") as f_out:
            for file_path in file_paths:
                if os.path.exists(file_path):
                    with open(file_path, "rb") as f_in:
                        f_out.write(f_in.read())
                else:
                    print(f"Warning: File not found at {file_path}")

    def decode(self):
        with gzip.open(self.output_file_path, "rb") as f_in:
            file_content = f_in.read()

        output_file_names = [
            self.avi_file_path,
            self.audio_file_path,
            self.mouse_events_file_path,
        ]

        for output_file_name in output_file_names:
            with open(output_file_name, "wb") as f_out:
                f_out.write(file_content)
