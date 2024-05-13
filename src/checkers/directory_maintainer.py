import os
from src.constants import OREAL_WORKING_DIR, OREAL_RECORDINGS_DIR


def fix_or_create_necessary_directories():
    # fix recording folder
    if not os.path.exists(OREAL_RECORDINGS_DIR):
        os.mkdir(OREAL_RECORDINGS_DIR)

    # fix working dir folder
    if not os.path.exists(OREAL_WORKING_DIR):
        os.mkdir(OREAL_WORKING_DIR)
