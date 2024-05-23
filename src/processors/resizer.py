from PIL import Image
import os

# Set the target size
target_width = 3840
target_height = 2160


# Function to resize images by cropping
def crop_backgrounds(input_folder, output_folder):
    for filename in os.listdir(input_folder):
        if filename.endswith(".jpg") or filename.endswith(
            ".png"
        ):  # Adjust file formats as needed
            with Image.open(os.path.join(input_folder, filename)) as img:
                width, height = img.size
                left = (width - target_width) / 2
                top = (height - target_height) / 2
                right = (width + target_width) / 2
                bottom = (height + target_height) / 2
                cropped_img = img.crop((left, top, right, bottom))
                cropped_img.save(os.path.join(output_folder, filename))


def create_thumbnails(input_folder, output_folder):
    for filename in os.listdir(input_folder):
        if filename.endswith(".jpg") or filename.endswith(
            ".png"
        ):  # Adjust file formats as needed
            with Image.open(os.path.join(input_folder, filename)) as img:

                cropped_img = img.resize((target_width // 6, target_height // 6))
                cropped_img.save(os.path.join(output_folder, filename))


if __name__ == "__main__":
    # Specify input and output folders
    bkgrnd_fldr = "D:\\Projects\\OReal\\assets\\backgrounds"
    tmbnil_fldr = "D:\\Projects\\OReal\\assets\\background_previews"

    # Call the function to resize images
    crop_backgrounds(bkgrnd_fldr, bkgrnd_fldr)
    create_thumbnails(bkgrnd_fldr, tmbnil_fldr)
