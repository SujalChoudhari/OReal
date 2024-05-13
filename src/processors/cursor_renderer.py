import cv2
import pyautogui
import datetime
import numpy as np
from PIL import Image


class CursorRenderer:
    def __init__(self, cursor_image):
        self.cursor_image = cursor_image

    def render_cursor(self, frame):
        cursor_pos = pyautogui.position()
        try:
            cursor_pil = Image.open(self.cursor_image)
            cursor_np = np.array(cursor_pil)
            cursor_rgb = cursor_np[:, :, :3]
            alpha_channel = cursor_np[:, :, 3]
            cursor_height, cursor_width = cursor_rgb.shape[:2]
            roi = frame[
                cursor_pos[1] : cursor_pos[1] + cursor_height,
                cursor_pos[0] : cursor_pos[0] + cursor_width,
            ]
            roi_height, roi_width = roi.shape[:2]
            roi_height, roi_width = max(1, roi_height), max(1, roi_width)
            cursor_resized = cv2.resize(cursor_rgb, (roi_width, roi_height))
            alpha_mask = alpha_channel / 255.0
            alpha_mask = np.expand_dims(alpha_mask, axis=-1)
            blended_cursor = alpha_mask * cursor_resized + (1 - alpha_mask) * roi
            frame[
                cursor_pos[1] : cursor_pos[1] + cursor_height,
                cursor_pos[0] : cursor_pos[0] + cursor_width,
            ] = blended_cursor
        except ValueError as e:
            pass
