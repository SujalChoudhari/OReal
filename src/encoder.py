import os

from src.constants import (
    OREAL_COMPLETE_AVI_FILE_EXT,
    OREAL_DEFAULT_VIDEO_EXT,
    OREAL_MOUSE_EVENT_EXT,
    OREAL_COMPLETE_FILE_HEADER,
)


class Encoder:
    def __init__(self, file_path):
        self.file_path = file_path + "." + OREAL_DEFAULT_VIDEO_EXT

    def encode(self):
        # Extract directory and base name from the file path
        directory, base_name = os.path.split(self.file_path)

        # Construct the paths for .avi and .orip files
        avi_file_path = self.file_path
        oreal_mouse_events_file_path = os.path.join(
            directory, os.path.splitext(base_name)[0] + "." + OREAL_MOUSE_EVENT_EXT
        )

        try:
            # Create the merged file path
            merged_file_path = os.path.join(
                directory,
                f"{os.path.splitext(base_name)[0]}.{OREAL_COMPLETE_AVI_FILE_EXT}",
            )

            # Open files for reading and writing
            with open(avi_file_path, "rb") as avi_file, open(
                oreal_mouse_events_file_path, "rb"
            ) as oreal_mouse_event_file, open(merged_file_path, "wb") as merged_file:
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

            return merged_file_path
        except FileNotFoundError as e:
            print("File not found.", e)
            return None

    def decode(self):
        merged_file_path = self.file_path.replace(
            f".{OREAL_DEFAULT_VIDEO_EXT}", f".{OREAL_COMPLETE_AVI_FILE_EXT}"
        )

        # Extract directory and base name from the merged file path
        directory, base_name = os.path.split(merged_file_path)

        # Construct the paths for decoded files
        decoded_avi_file_path = os.path.join(
            directory, f"{os.path.splitext(base_name)[0]}.{OREAL_DEFAULT_VIDEO_EXT}"
        )
        decoded_oreal_mouse_events_file_path = os.path.join(
            directory, f"{os.path.splitext(base_name)[0]}.{OREAL_MOUSE_EVENT_EXT}"
        )

        try:
            # Open the merged file for reading
            with open(merged_file_path, "rb") as merged_file:
                # Check for OREAL header
                header = merged_file.read(5)
                if header != OREAL_COMPLETE_FILE_HEADER.encode("ascii"):
                    print("Invalid encoded file format.")
                    return None

                # Initialize flag to indicate when to switch to OREAL_MOUSE_EVENT content
                events_started = False

                # Open files for writing decoded content
                with open(decoded_avi_file_path, "wb") as avi_file, open(
                    decoded_oreal_mouse_events_file_path, "wb"
                ) as oreal_mouse_event_file:
                    # Read merged content and write to appropriate files
                    for line in merged_file:
                        if line.strip() == b"EVENTS_START":
                            events_started = True
                            continue
                        if not events_started:
                            avi_file.write(line)
                        else:
                            oreal_mouse_event_file.write(line)

            return decoded_avi_file_path, decoded_oreal_mouse_events_file_path
        except FileNotFoundError as e:
            print("File not found.", e)
            return None
