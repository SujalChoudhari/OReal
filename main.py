from app import Application
from src.processors.encoder import Encoder

def main() -> None:
    app = Application()
    app.start()
    app.run()


if __name__ == "__main__":
    # main()
    Encoder("recordings\FantasticVisuals","recordings\FantasticVisuals").decode()
