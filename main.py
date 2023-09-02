import os
import pandas as pd
import folium
import webbrowser


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
    colors = ['blue', 'green', 'red', 'purple', 'orange', 'pink', 'brown', 'gray']

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
            # Plot GPS coordinates as markers
            for index, row in df.iterrows():
                lat, lon = row['GPS'].split()
                lat = float(lat)
                lon = float(lon)
                coords.append([lat, lon])
                folium.CircleMarker(
                    location=[lat, lon],
                    radius=5,
                    # color=colors[idx % len(colors)],
                    # fill_color=colors[idx % len(colors)],
                    fill=True,
                    fill_opacity=0.7,
                    # popup=final_coord
                ).add_to(fg)

            # Add a line connecting the points
            folium.PolyLine(
                locations=coords,
                # color=colors[idx % len(colors)],
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
