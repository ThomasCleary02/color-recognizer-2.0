from collections import Counter
from PIL import Image

def get_dominant_color(image, num_colors=1):
    reduced = image.convert('P', palette=Image.Palette.ADAPTIVE, colors=256)
    reduced = reduced.convert('RGB')
    pixels = list(reduced.getdata())
    color_counts = Counter(pixels)
    dominant_colors = sorted(color_counts.items(), key=lambda x: x[1], reverse=True)
    
    return dominant_colors[:num_colors]

def analyze_snippet(image, left, top, right, bottom, num_colors=5):
    img = Image.open(image)
    cropped_image = img.crop((left, top, right, bottom))
    dominant_colors = get_dominant_color(cropped_image, num_colors)
    color_analysis = []
    total_pixels = sum(count for _, count in dominant_colors)
    for color, count in dominant_colors:
        percentage = (count / total_pixels) * 100
        color_info = {
            'rgb': color,
            'hex': '#{:02x}{:02x}{:02x}'.format(*color),
            'percentage': round(percentage, 2),
        }
        color_analysis.append(color_info)
    
    return color_analysis