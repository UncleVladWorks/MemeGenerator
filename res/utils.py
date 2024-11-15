import requests
from PIL import Image, ImageDraw, ImageFont, ImageEnhance
from io import BytesIO
import os


def wrap_text_to_fit_width(text, font, max_width):
    lines = []
    words = text.split()
    while words:
        line = ''
        while words and font.getsize(line + words[0])[0] <= max_width:
            line += (words.pop(0) + ' ')
        lines.append(line)
    return lines

def text_wrap(text, font, max_width):
    lines = []
    words = text.split()
    current_line = []

    for word in words:
        test_line = current_line + [word] if current_line else [word]
        test_size = font.getsize(' '.join(test_line))

        if test_size[0] <= max_width:
            current_line.append(word)
        else:
            lines.append(' '.join(current_line))
            current_line = [word]

    if current_line:
        lines.append(' '.join(current_line))

    return lines

def position_multiline_text(lines, initial_y, font):
    line_height = font.getsize(lines[0])[1]
    total_height = len(lines) * line_height
    return initial_y - (total_height - line_height) / 2  # Center-align the multiline text

def draw_multiline_text(draw, center_x, y, lines, font, fill):
    line_height = font.getsize(lines[0])[1]
    for line in lines:
        text_width, _ = font.getsize(line)
        x = center_x - text_width // 2
        draw.text((x, y), line, font=font, fill=fill)
        y += line_height

def get_average_brightness(image):
    grayscale_image = image.convert('L')
    histogram = grayscale_image.histogram()
    pixels = sum(histogram)
    brightness = scale = len(histogram)

    for index in range(0, scale):
        ratio = histogram[index] / pixels
        brightness += ratio * (-scale + index)

    return brightness / scale


def adjust_image_brightness(image, threshold=128, enhance_factor_dark=0.7, enhance_factor_bright=1.3):
    """Adjusts the image brightness based on its average brightness.

    If average brightness is above the threshold, the image is made brighter.
    Otherwise, it's made darker.
    """
    average_brightness = get_average_brightness(image)

    enhancer = ImageEnhance.Brightness(image)

    if average_brightness > threshold:
        return enhancer.enhance(enhance_factor_bright)
    else:
        return enhancer.enhance(enhance_factor_dark)

def download_image_and_two_texts(url, top_text, bottom_text, output_path, fontsize, data_path, id_):
    response = requests.get(url)
    image = Image.open(BytesIO(response.content))

    # Adjust image brightness
    image = adjust_image_brightness(image)

    # Create a drawing context
    draw = ImageDraw.Draw(image)

    # Calculate the maximum width for the text
    max_text_width = image.width - 20  # Allow for a small margin on both sides

    # Load the font
    font = ImageFont.truetype("res/fonts/Roboto/Roboto-Bold.ttf", fontsize)

    # Determine text color based on image colors
    # Here, we'll use a simple approach by choosing white or black depending on the image's average brightness
    # image_gray = image.convert('L')  # Convert the image to grayscale
    # average_brightness = image_gray.getpixel((image.width // 2, image.height // 2))  # Sample a pixel from the center
    average_brightness = get_average_brightness(image)
    text_color = 'white' if average_brightness < 128 else 'black'

    # Calculate text size for top and bottom text
    top_text_size = font.getsize(top_text)
    bottom_text_size = font.getsize(bottom_text)

    # Calculate the position for the top text to center it horizontally and vertically
    top_text_x = (image.width - top_text_size[0]) // 2
    top_text_y = (image.height - top_text_size[1]) // 16

    # Calculate the position for the bottom text to center it horizontally and vertically
    bottom_text_x = (image.width - bottom_text_size[0]) // 2
    bottom_text_y = (image.height - bottom_text_size[1]) // 1.1  # Adjust the vertical position as needed

    # Calculate the center x position for top and bottom text
    center_x = image.width // 2

    # Split the text into multiple lines if it's too long to fit within the width
    top_text_lines = text_wrap(top_text, font, max_text_width)
    bottom_text_lines = text_wrap(bottom_text, font, max_text_width)

    # Calculate vertical positions for multiline text
    top_text_y = position_multiline_text(top_text_lines, top_text_y, font)
    bottom_text_y = position_multiline_text(bottom_text_lines, bottom_text_y, font)

    # Draw the multiline text on the image
    draw_multiline_text(draw, center_x, top_text_y, top_text_lines, font, text_color)
    draw_multiline_text(draw, center_x, bottom_text_y, bottom_text_lines, font, text_color)

    # Save the final image
    image.save(output_path)

def download_image_and_add_text(url, text, output_path, fontsize, data_path, id_):
    response = requests.get(url)
    image = Image.open(BytesIO(response.content))

    # Save the raw image
    image.save(os.path.join(data_path, 'images', f'{id_}.jpg'))

    # Prepare drawing context
    draw = ImageDraw.Draw(image)
    font_regular = ImageFont.truetype("res/fonts/Roboto/Roboto-Regular.ttf", fontsize)
    font_bold = ImageFont.truetype("res/fonts/Roboto/Roboto-Bold.ttf", fontsize)

    max_rectangle_width = image.width * 0.9

    # Calculate text size and position
    lines = wrap_text_to_fit_width(text, font_bold, max_rectangle_width)
    text_height_total = 0
    max_text_width = 0
    line_heights = []

    for line in lines:
        text_width, text_height = draw.textsize(line, font_bold)
        max_text_width = max(max_text_width, text_width)
        text_height_total += text_height
        line_heights.append(text_height)

    rectangle_height = text_height_total + 20

    # Resize text if it doesn't fit in the rectangle
    if max_text_width > max_rectangle_width:
        new_font_size = int(30 * (max_rectangle_width / max_text_width))
        new_font_size = max(new_font_size, fontsize)  # Ensure font size doesn't go below fixed size
        font_regular = ImageFont.truetype("res/fonts/Roboto/Roboto-Regular.ttf", new_font_size)
        font_bold = ImageFont.truetype("res/fonts/Roboto/Roboto-Bold.ttf", new_font_size)
        max_text_width = int(max_text_width * (max_rectangle_width / max_text_width))
        text_height_total = int(text_height_total * (max_rectangle_width / max_text_width))
        rectangle_height = text_height_total + 20
        line_heights = [int(h * (max_rectangle_width / max_text_width)) for h in line_heights]

    # Create a new image with the same width as the original image but with extra height
    new_image = Image.new("RGB", (image.width, image.height + rectangle_height), (255, 255, 255))

    # Paste the original image at the top of the new image
    new_image.paste(image, (0, 0))

    # Create a grey-blue rectangle at the bottom of the new image
    draw = ImageDraw.Draw(new_image)
    draw.rectangle([(0, image.height), (image.width, image.height + rectangle_height)], fill=(70, 130, 180))

    # Define margin
    margin = 10

    # 1. Initial Text Size Calculation
    lines = wrap_text_to_fit_width(text, font_bold, max_rectangle_width)
    text_height_total = sum([draw.textsize(line, font=font_bold)[1] for line in lines])

    # 2. Adjust Rectangle Height
    rectangle_height = text_height_total + 2 * margin  # Consider margin on top and bottom

    # Calculate the total spacing available (subtract text and margins)
    total_spacing = rectangle_height - text_height_total - 2 * margin

    # Distribute the spacing evenly between lines
    if len(lines) > 1:  # To avoid division by zero
        spacing = total_spacing / (len(lines) - 1)
    else:
        spacing = total_spacing  # If only one line, spacing is all the available space

    # 3. Create a New Image
    new_image = Image.new("RGB", (image.width, image.height + rectangle_height), (255, 255, 255))
    new_image.paste(image, (0, 0))

    # Create a grey-blue rectangle at the bottom of the new image
    draw = ImageDraw.Draw(new_image)
    draw.rectangle([(0, image.height), (image.width, image.height + rectangle_height)], fill=(70, 130, 180))

    # 4. Render Text
    y = image.height + margin
    for line in lines:
        font = font_bold
        text_width, text_height = draw.textsize(line, font=font)
        x = (image.width - text_width) // 2
        draw.text((x, y), line, font=font, fill=(255, 255, 255))
        y += text_height + spacing

    # Save the new image
    new_image.save(output_path)