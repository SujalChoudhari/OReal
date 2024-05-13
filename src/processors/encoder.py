import os
import wave

from src.constants import (
    OREAL_FILE_EXT,
    OREAL_DEFAULT_VIDEO_EXT,
    OREAL_MOUSE_EVENT_EXT,
    OREAL_COMPLETE_FILE_HEADER,
    OREAL_DEFAULT_AUDIO_EXT,
)


class Encoder:
    """
    Proposed Header format:
    - OREAL
    - [VideoPresenter] 1b (0 = not present, 1 = present)
    - [EventPresent] 1b (0 = not present, 1 = present)
    - [AudioPresent] 1b (0 = not present, 1 = present)

    only present if [AudioPresent] == 1
    - [AudioChannel] 1b (1 = mono, 2 = stereo)
    - [AudioSampleRate] 4b (22050 = 22050 Hz, 44100 = 44100 Hz)
    - [AudioSampleWidth] 1b (1 = 8-bit, 2 = 16-bit)
    """

    def __init__(self, file_path: str, output_file_path: str = None) -> None:
        """Paths should be without extension"""
        self.avi_file_path = file_path + "." + OREAL_DEFAULT_VIDEO_EXT
        self.audio_file_path = file_path + "." + OREAL_DEFAULT_AUDIO_EXT
        self.mouse_events_file_path = file_path + "." + OREAL_MOUSE_EVENT_EXT

        if output_file_path is None:
            self.output_file_path = file_path + "." + OREAL_FILE_EXT
        else:
            self.output_file_path = output_file_path + "." + OREAL_FILE_EXT

    def encode(self):
        # Extract directory and base name from the file path
        directory, base_name = os.path.split(self.avi_file_path)

        try:
            # Open files for reading and writing
            with open(self.avi_file_path, "rb") as avi_file, open(
                self.mouse_events_file_path, "rb"
            ) as oreal_mouse_event_file, open(
                self.output_file_path, "wb"
            ) as merged_file:
                # Write OREAL header
                merged_file.write(OREAL_COMPLETE_FILE_HEADER.encode("ascii"))

                # Write AVI content
                for chunk in avi_file:
                    merged_file.write(chunk)

                # Write separator
                merged_file.write(b"\nEVENTS_START\n")

                # Write OREAL_MOUSE_EVENT content
                for line in oreal_mouse_event_file:
                    merged_file.write(line)

                # Check if WAV file exists
                if os.path.exists(self.audio_file_path):
                    # Write separator
                    merged_file.write(b"\nAUDIO_START\n")

                    # Open and write audio content
                    with wave.open(self.audio_file_path, "rb") as audio_file:
                        merged_file.write(
                            audio_file.readframes(audio_file.getnframes())
                        )

            return self.output_file_path
        except FileNotFoundError as e:
            print("File not found.", e)
            return None

    def decode(self):

        # Extract directory and base name from the merged file path
        directory, base_name = os.path.split(self.audio_file_path)

        try:
            # Open the merged file for reading
            with open(self.audio_file_path, "rb") as merged_file:
                # Check for OREAL header
                header = merged_file.read(5)
                if header != OREAL_COMPLETE_FILE_HEADER.encode("ascii"):
                    print("Invalid encoded file format.")
                    return None

                # Initialize flags to indicate when to switch to OREAL_MOUSE_EVENT and audio content
                events_started = False
                audio_started = False

                # Open files for writing decoded content
                with open(self.avi_file_path, "wb") as avi_file, open(
                    self.mouse_events_file_path, "wb"
                ) as oreal_mouse_event_file:
                    # Set audio parameters if audio content exists
                    audio_content_pos = None
                    audio_file = None
                    while True:
                        line = merged_file.readline()
                        if not line:
                            break
                        if line.strip() == b"EVENTS_START":
                            events_started = True
                            continue
                        elif line.strip() == b"AUDIO_START":
                            audio_started = True
                            # Set the position of audio content start
                            audio_content_pos = merged_file.tell()
                            continue
                        if not events_started:
                            avi_file.write(line)
                        elif not audio_started:
                            oreal_mouse_event_file.write(line)
                        elif audio_started and audio_content_pos is not None:
                            # Open and write audio content if it exists
                            if audio_file is None:
                                audio_file = wave.open(self.audio_file_path, "wb")
                                audio_file.setnchannels(2)  # Assuming stereo audio
                                audio_file.setsampwidth(
                                    2
                                )  # 2 bytes per sample (16-bit)
                                audio_file.setframerate(
                                    44100
                                )  # Sample rate of 44.1 kHz
                            merged_file.seek(audio_content_pos)
                            audio_file.writeframes(merged_file.read())
                            break  # No need to read further after writing audio content

            return (
                self.avi_file_path,
                self.mouse_events_file_path,
                self.audio_file_path if audio_content_pos is not None else None,
            )
        except FileNotFoundError as e:
            print("File not found.", e)
            return None
