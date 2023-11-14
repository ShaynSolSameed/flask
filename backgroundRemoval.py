from rembg import remove
from PIL import Image


def removeBackground(inputPath):
    originalImage = Image.open(inputPath)
    removed = remove(originalImage)

    whiteBackground = Image.new("RGB", removed.size, (255, 255, 255))

    # Paste the removed foreground onto the white background
    finalImage = Image.alpha_composite(
        whiteBackground.convert('RGBA'), removed)

    finalImage = finalImage.convert('RGB')

    finalImage = finalImage.crop(removed.getbbox())
    finalImage.save(inputPath)


# Call the function with the path to your image

inputPath = "1.jpg"
removeBackground(inputPath)
