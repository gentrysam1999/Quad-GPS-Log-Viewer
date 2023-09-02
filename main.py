import os
import pandas as pd
import folium
import webbrowser
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap


# Function to create a rainbow gradient color map and return unique colors based on the input number
def create_rainbow_colormap(num_colors):
    colors = [(1, 0, 0), (1, 1, 0), (0, 1, 0), (0, 1, 1), (0, 0, 1), (1, 0, 1)]
    n = len(colors)
    gradient = []
    for i in range(n - 1):
        for j in range(num_colors // n):
            r = (colors[i][0] * (n - j - 1) + colors[i + 1][0] * j) / (n - 1)
            g = (colors[i][1] * (n - j - 1) + colors[i + 1][1] * j) / (n - 1)
            b = (colors[i][2] * (n - j - 1) + colors[i + 1][2] * j) / (n - 1)
            gradient.append((r, g, b))
    return LinearSegmentedColormap.from_list('rainbow', gradient, num_colors)


# Function to read CSV files in a folder and plot GPS coordinates
def plot_gps_coordinates(folder_path):
    # Create a map
    tile = folium.TileLayer(
        tiles='https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}',
        attr='Esri',
        name='Esri Satellite',
        max_zoom=19,
        detect_retina=True,
        overlay=False,
        control=True
    )
    m = folium.Map(location=[0, 0], zoom_start=2, tiles=tile)

    # Add OpenStreetMap tile layer
    folium.TileLayer(tiles="OpenStreetMap").add_to(m)

    # List of available colors for different CSV files
    num_files = len([filename for filename in os.listdir(folder_path) if filename.endswith('.csv')])
    colormap = create_rainbow_colormap(num_files)

    # Iterate over CSV files in the folder
    for idx, filename in enumerate(os.listdir(folder_path)):
        if filename.endswith('.csv'):
            file_path = os.path.join(folder_path, filename)

            # Read the CSV file into a Pandas DataFrame
            df = pd.read_csv(file_path)
            df = df.dropna()
            if len(df['GPS']) == 0:
                continue

            # Create a feature group for each CSV file
            final_coord = df['GPS'].iloc[-1]
            fg = folium.FeatureGroup(name=final_coord, overlay=True, control=True)
            coords = []

            # Get a color from the colormap
            color = colormap(idx)
            r, g, b, a = color
            color = f"rgba({r},{g},{b},{a})"
            print(color)

            # Plot GPS coordinates as markers
            for index, row in df.iterrows():
                lat, lon = row['GPS'].split()
                lat = float(lat)
                lon = float(lon)
                coords.append([lat, lon])
                folium.CircleMarker(
                    location=[lat, lon],
                    radius=5,
                    color=color,
                    fill_color=color,
                    fill=True,
                    fill_opacity=0.7,
                    # popup=final_coord
                ).add_to(fg)

            # Add a line connecting the points
            folium.PolyLine(
                locations=coords,
                color=color,
                weight=2,
                opacity=0.7,
            ).add_to(fg)
            # Add a Marker for the last Coordinate
            folium.Marker(
                location=final_coord.split(),
                popup=final_coord
            ).add_to(fg)

            fg.add_to(m)

    # Add layer control to toggle CSV files on/off
    folium.LayerControl().add_to(m)

    # Save the map to an HTML file
    map_filename = 'gps_coordinates_map.html'
    m.save(os.path.join(folder_path, map_filename))
    # Open Map in Web Browser
    webbrowser.open_new_tab(f'file://{os.path.realpath(os.path.join(folder_path, map_filename))}')


if __name__ == "__main__":
    folder_path = input("Enter the folder path containing CSV files: ")
    plot_gps_coordinates(folder_path)
    print("Map saved as 'gps_coordinates_map.html'.")
