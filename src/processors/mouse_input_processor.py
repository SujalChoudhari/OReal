import os
from src.constants import OREAL_MOUSE_EVENT_EXT, OREAL_WORKING_DIR


class MouseInputProcessor:

    def __init__(self) -> None:
        self.MAX_ZOOM_AMOUNT = 2.0
        self.zoom_array = []
        self.scaled_array = []
        self.parts = []

    def generate_zooming_values(self, smoothness=10):
        parts = self._parse_mouse_event_file()
        clicks = [x[3] for x in parts]
        self.zoom_array = self._process_zoom_level(
            clicks, smoothness=smoothness * smoothness // 100
        )  # parabolic curve
        return self.zoom_array

    def generate_mouse_size_values(self, smoothness=10):
        parts = self._parse_mouse_event_file()
        cords = [(float(x[1]), float(x[2])) for x in parts]
        self.scaled_array = self._process_mouse_size(
            cords, smoothness=smoothness * smoothness // 100
        )  # parabolic curve
        return self.scaled_array

    def save_to_file(self):
        self._clear_file()
        # iter over parts, zoom array and scaled array
        for i in range(len(self.parts)):
            line = f"{self.parts[i][0]} {self.parts[i][1]} {self.parts[i][2]} {self.parts[i][2]} {self.zoom_array[i]} {self.scaled_array[i]}\n"
            self._append_to_file(line)

    def _get_mouse_event_file_contents(self):
        try:
            filename = next(
                x
                for x in os.listdir(OREAL_WORKING_DIR)
                if x.endswith(OREAL_MOUSE_EVENT_EXT)
            )
        except StopIteration:
            raise FileNotFoundError("Mouse event file not found.")

        with open(os.path.join(OREAL_WORKING_DIR, filename), "r") as f:
            return f.read()

    def _parse_mouse_event_file(self):
        content = self._get_mouse_event_file_contents()
        lines = content.split("\n")
        parts = [x.strip().split() for x in lines if x.strip()]
        self.parts = parts
        return parts

    def _clear_file(self):
        try:
            filename = next(
                x
                for x in os.listdir(OREAL_WORKING_DIR)
                if x.endswith(OREAL_MOUSE_EVENT_EXT)
            )
        except StopIteration:
            raise FileNotFoundError("Mouse event file not found.")

        with open(os.path.join(OREAL_WORKING_DIR, filename), "w") as f:
            f.write("")

    def _append_to_file(self, line: str):
        try:
            filename = next(
                x
                for x in os.listdir(OREAL_WORKING_DIR)
                if x.endswith(OREAL_MOUSE_EVENT_EXT)
            )
        except StopIteration:
            raise FileNotFoundError("Mouse event file not found.")

        with open(os.path.join(OREAL_WORKING_DIR, filename), "a") as f:
            f.write(line)

    def _process_zoom_level(self, clicks: list[str], smoothness=10) -> list[float]:
        zoom = []
        for i in range(len(clicks)):
            if clicks[i] == "True":
                zoom.append(self.MAX_ZOOM_AMOUNT)
            else:
                zoom.append(1)

        zoom[0] = 1
        zoom[-1] = 1

        return self._smooth_values(zoom, smoothness=smoothness)

    def _process_mouse_size(
        self, cords: tuple[float, float], smoothness=10
    ) -> list[float]:
        sizes = []
        for i in range(len(cords)):
            velocity_x = float(cords[i][0]) - (float(cords[i - 1][0]) if i > 0 else 0)
            velocity_y = float(cords[i][1]) - (float(cords[i - 1][1]) if i > 0 else 0)
            velocity = (velocity_x**2 + velocity_y**2) ** 0.5
            velocity = min(1 / velocity if velocity > 0 else 0, 1)

            size = 1 + velocity * self.MAX_ZOOM_AMOUNT
            sizes.append(size)

        sizes[0] = 1
        sizes[-1] = 1

        return self._smooth_values(sizes, smoothness=smoothness)

    def _smooth_values(self, array: list[float], smoothness) -> list[float]:
        smoothed_values = [float(a) for a in array]  # Initialize with original values

        for _ in range(int(smoothness)):
            new_smoothed_values = smoothed_values.copy()

            for i in range(1, len(smoothed_values) - 1):
                prev_value = smoothed_values[i - 1]
                curr_value = smoothed_values[i]
                next_value = smoothed_values[i + 1]

                # Calculate the running average
                new_value = (prev_value + curr_value + curr_value + next_value) / 4
                new_smoothed_values[i] = new_value

            # Update the smoothed values for the next iteration
            smoothed_values = new_smoothed_values

        # Scale the final output to ensure the highest point is at 2.0 and the lowest is at 1.0
        max_value = max(smoothed_values)
        min_value = min(smoothed_values)
        scale_factor = (2.0 - 1.0) / (max_value - min_value)
        scaled_smoothed_values = [
            1.0 + (value - min_value) * scale_factor for value in smoothed_values
        ]

        return scaled_smoothed_values
