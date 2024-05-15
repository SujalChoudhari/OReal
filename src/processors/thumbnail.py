import pyautogui
from src.constants import OREAL_WORKING_DIR


def generate_thumbnail(filename: str):
    img = pyautogui.screenshot()
    # compress it to half size
    img.thumbnail((img.width // 4, img.height // 4))
    img.save(OREAL_WORKING_DIR + filename)
