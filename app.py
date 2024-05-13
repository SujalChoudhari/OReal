from src.gui.app import OrealApp
from src.checkers.directory_maintainer import fix_or_create_necessary_directories

class Application:
    def __init__(self) -> None:
        self.app = OrealApp()

    def start(self):
        fix_or_create_necessary_directories()

    def run(self) -> None:
        self.app.run()
