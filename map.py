import numpy as np
import os
from matplotlib.colors import LinearSegmentedColormap
from PIL import Image, ImageDraw
from staticmap import StaticMap, IconMarker

# Create a custom colormap
aqi_levels = [0, 51, 101, 151, 201, 301, 500]
colors = ["#00FF00", "#FFFF00", "#FFA500", "#FF0000", "#800080", "#A52A2A"]
cmap = LinearSegmentedColormap.from_list("aqi_cmap", colors, N=500)

def aqi_to_color(aqi):
    """ Convert AQI value to an RGB color, respecting the AQI levels """
    # Ensure AQI is within the valid range
    aqi = np.clip(aqi, 0, 500)

    # Find the segment in which the AQI falls
    for i in range(1, len(aqi_levels)):
        if aqi <= aqi_levels[i]:
            break

    # Normalize AQI within its specific segment (linear interpolation)
    segment_min = aqi_levels[i-1]
    segment_max = aqi_levels[i]
    normalized_aqi = (aqi - segment_min) / (segment_max - segment_min)

    # Normalize for the colormap scale
    cmap_position = (i-1 + normalized_aqi) / (len(aqi_levels) - 1)

    # Get color from colormap and convert to RGB integers
    color = np.array(cmap(cmap_position)[:3])
    return (color * 255).astype(int)

def apply_aqi_overlay(map_image_path, aqi_value, output_image_path):
    """ Apply AQI color overlay to the map image """
    # Load the map image
    map_image = Image.open(map_image_path).convert('RGBA')
    width, height = map_image.size

    # Create an overlay image
    overlay = Image.new('RGBA', map_image.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)

    # Create a color for the overlay based on AQI
    color = aqi_to_color(aqi_value)
    overlay_color = (*color, 112)  # Add alpha for transparency

    # Draw the overlay
    draw.rectangle([0, 0, width, height], fill=overlay_color)

    # Combine the map image with the overlay
    combined = Image.alpha_composite(map_image, overlay)

    # Save the output image
    combined.save(output_image_path)

def generate_map_with_overlay(lat, lon, aqi_value, assets_path):
    """ Generate a map with an AQI overlay """
    # Create a StaticMap object with higher resolution and a cleaner map style
    map_image_path = os.path.join(assets_path, "temp_map.png")
    icon_image_path = os.path.join(assets_path, "icon.png")
    output_image_path = os.path.join(assets_path, "aqi_map.png")

    # Generate the map
    m = StaticMap(800, 600, url_template='http://a.basemaps.cartocdn.com/rastertiles/voyager/{z}/{x}/{y}.png')

    # Add a custom marker at the given lat, lon
    icon_marker = IconMarker((lon, lat), icon_image_path, 30, 30)
    m.add_marker(icon_marker)

    # Render the map and save it temporarily
    image = m.render(zoom=13)
    image.save(map_image_path, optimize=True, quality=95)

    # Apply the AQI overlay on top of the map and save it with the given image name
    apply_aqi_overlay(map_image_path, aqi_value, output_image_path)

    print(f"Map with AQI overlay has been saved as '{output_image_path}'")

# # Example usage
# generate_map_with_overlay(40.7128, -74.0060, 58, '../assets')