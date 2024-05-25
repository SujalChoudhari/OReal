from src.constants import (
    OREAL_DEFAULT_VIDEO_EXT,
    OREAL_MOUSE_EVENT_EXT,
    OREAL_DEFAULT_AUDIO_EXT,
    OREAL_BACKGROUNDS_DIR,
    OREAL_CURSOR_DIR,
    OREAL_WORKING_DIR,
)

from moviepy.editor import ImageClip, VideoFileClip, CompositeVideoClip, AudioFileClip
import pandas as pd
from tkinter import filedialog
import os


def make_video(background: str, cursor: str):
    background_complete_path = os.path.join(OREAL_BACKGROUNDS_DIR, background)
    cursor_complete_path = os.path.join(OREAL_CURSOR_DIR, cursor)

    # Open mouse events file from the working directory
    mouse_path = os.path.join(
        OREAL_WORKING_DIR,
        next(
            x
            for x in os.listdir(OREAL_WORKING_DIR)
            if x.endswith(OREAL_MOUSE_EVENT_EXT)
        ),
    )

    # Open audio file from the working directory, if it exists
    try:
        audio_path = os.path.join(
            OREAL_WORKING_DIR,
            next(
                x
                for x in os.listdir(OREAL_WORKING_DIR)
                if x.endswith(OREAL_DEFAULT_AUDIO_EXT)
            ),
        )
        audio_exists = True
    except StopIteration:
        audio_exists = False

    avi_path = os.path.join(
        OREAL_WORKING_DIR,
        next(
            x
            for x in os.listdir(OREAL_WORKING_DIR)
            if x.endswith(OREAL_DEFAULT_VIDEO_EXT)
        ),
    )

    background_image = ImageClip(background_complete_path)
    cursor_image = ImageClip(cursor_complete_path)
    mouse_events = pd.read_csv(mouse_path, delim_whitespace=True, header=None)
    video = VideoFileClip(avi_path)

    def process_frame(get_frame, t):
        frame = get_frame(t)
        frame_clip = ImageClip(frame).set_duration(1 / video.fps)
        frame_width, frame_height, _ = frame.shape

        # Find the closest mouse event time to the current frame time
        mouse_event_index = int(t * video.fps)
        if mouse_event_index >= len(mouse_events):
            mouse_event_index = len(mouse_events) - 1

        # Get mouse event details
        x = mouse_events.iloc[mouse_event_index, 1]
        y = mouse_events.iloc[mouse_event_index, 2]
        zoom = mouse_events.iloc[mouse_event_index, 4]
        scale = mouse_events.iloc[mouse_event_index, 5]

        # Calculate cursor position and scaling
        cursor_position = (
            x - cursor_image.w * scale / 2,
            y - cursor_image.h * scale / 2,
        )
        positioned_cursor_image = cursor_image.set_position(cursor_position).resize(
            scale
        )

        # Overlay the cursor on the frame
        vid_with_cursor = CompositeVideoClip([frame_clip, positioned_cursor_image])

        # Zoom video (zoom factor is between 1 and 2)
        zoom_factor = zoom

        # Calculate the new size of the frame after zoom
        new_frame_width = vid_with_cursor.w * zoom_factor
        new_frame_height = vid_with_cursor.h * zoom_factor

        # Calculate the position to center the zoomed frame within the background
        video_pos = (
            (vid_with_cursor.w / 2) - (x * zoom_factor),
            (vid_with_cursor.h / 2) - (y * zoom_factor),
        )

        # Scale the frame and reposition it
        zoomed_vid_with_cursor = (
            ImageClip(vid_with_cursor.get_frame(0))
            .resize(zoom_factor)
            .set_position(video_pos)
        )

        # Calculate the centered position of the video on the background
        final_video_pos = (
            (background_image.w - new_frame_width) / 2,
            (background_image.h - new_frame_height) / 2,
        )

        # Create a frame with the background and the centered video with cursor
        return CompositeVideoClip(
            [
                background_image.set_duration(1 / video.fps),
                zoomed_vid_with_cursor.set_position(final_video_pos),
            ]
        ).get_frame(0)

    # Create the final video with the cursor overlay and centered on the background
    final_video = video.fl(process_frame)

    # Add audio if it exists
    if audio_exists:
        audio = AudioFileClip(audio_path)
        final_video = final_video.set_audio(audio)

    output_path = filedialog.asksaveasfilename(
        title="Save Video As",
        defaultextension=".mp4",
        filetypes=[("MP4 files", "*.mp4"), ("All files", "*.*")],
    )

    if output_path:
        final_video.write_videofile(output_path, codec="libx264")
