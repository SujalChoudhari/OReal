import os
from src.constants import OREAL_MOUSE_EVENT_EXT, OREAL_WORKING_DIR


class MouseInputProcessor:

    MAX_ZOOM_AMOUNT = 2.0
    ZOOM_INCREMENTER = 0.1

    def get_mouse_event_file_contents(self):
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

    def parse_mouse_event_file(self):
        content = self.get_mouse_event_file_contents()
        lines = content.split("\n")
        parts = [x.strip().split() for x in lines if x.strip()]
        return parts

    def clear_file(self):
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

    def append_to_file(self, line: str):
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

    def process_mouse_events(self, zoom_smoothness=10,scale_smoothness=10):
        parts = self.parse_mouse_event_file()
        # remove the 4 and 5th column if present
        for i in range(len(parts)):
            if len(parts[i]) > 5:
                parts[i].pop(4)
                parts[i].pop(4)
            elif len(parts[i]) > 4:
                parts[i].pop(4)

        self.process_zoom_level(parts, smoothness=zoom_smoothness)
        self.process_mouse_size(parts, smoothness=scale_smoothness)
        mouse_size_array = [float(x[5]) for x in parts]
        zoom_level_array = [float(x[4]) for x in parts]
        self.clear_file()

        for line in parts:
            self.append_to_file(
                f"{line[0]} {line[1]} {line[2]} {line[3]} {line[4]} {line[5]}\n"
            )

        return zoom_level_array, mouse_size_array

    def process_zoom_level(self, parts, smoothness=10):
        for i in range(len(parts)):
            if parts[i][3] == "True":
                parts[i].append(self.MAX_ZOOM_AMOUNT)
            else:
                parts[i].append(1)

        self.smooth_values(parts, index=4, smoothness=smoothness)

    def process_mouse_size(self, parts, smoothness=10):
        for i in range(len(parts)):
            velocity_x = float(parts[i][1]) - (float(parts[i - 1][1]) if i > 0 else 0)
            velocity_y = float(parts[i][2]) - (float(parts[i - 1][2]) if i > 0 else 0)
            velocity = (velocity_x**2 + velocity_y**2) ** 0.5
            velocity = min(1 / velocity if velocity > 0 else 0, 1)

            size = 1 + velocity * self.MAX_ZOOM_AMOUNT
            parts[i].append(size)
        parts[0][3] = "False"
        parts[-1][3] = "False"

        self.smooth_values(parts, index=5, smoothness=smoothness)
    def smooth_values(self, parts, index, smoothness):
        smoothed_values = [float(part[index]) for part in parts]  # Initialize with original values

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
        scaled_smoothed_values = [1.0 + (value - min_value) * scale_factor for value in smoothed_values]

        for i in range(len(parts)):
            parts[i][index] = str(scaled_smoothed_values[i])