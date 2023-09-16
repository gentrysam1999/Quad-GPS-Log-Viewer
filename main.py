import os
import pandas as pd
import folium
import webbrowser
import calculations
from datetime import datetime, timedelta
from statistics import mean


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

            if df['GPS'].dtype != object:
                continue

            # Create a feature group for each CSV file
            final_coord = df['GPS'].iloc[-1]

            fg = folium.FeatureGroup(name=final_coord, overlay=True, control=True)

            # Initialise variables
            home_lat, home_lon = df['GPS'].iloc[0].split()
            home_lat = float(home_lat)
            home_lon = float(home_lon)
            home_height = float(df['Alt(m)'].iloc[0])
            prev_row = None
            coords = []
            change_in_distances = []
            change_in_times = []
            speeds = []
            heights = []
            distances_to_home = []

            # Plot GPS coordinates as markers
            for index, row in df.iterrows():
                lat, lon = row['GPS'].split()
                lat = float(lat)
                lon = float(lon)
                height = float(row['Alt(m)'])
                time = datetime.strptime(row['Time'], '%H:%M:%S.%f')
                dist_to_home = 0
                velocity = 0
                coords.append([lat, lon])
                heights.append(height)

                if prev_row is not None:
                    prev_lat, prev_lon = prev_row['GPS'].split()
                    prev_lat = float(prev_lat)
                    prev_lon = float(prev_lon)
                    prev_height = float(prev_row['Alt(m)'])
                    prev_time = datetime.strptime(prev_row['Time'], '%H:%M:%S.%f')
                    time_diff = (time - prev_time).total_seconds()
                    change_in_times.append(time_diff)
                    distance_diff = calculations.distance_calc(prev_lat,
                                                               prev_lon,
                                                               prev_height,
                                                               lat,
                                                               lon,
                                                               height)
                    change_in_distances.append(distance_diff)
                    dist_to_home = calculations.distance_calc(home_lat,
                                                              home_lon,
                                                              home_height,
                                                              lat,
                                                              lon,
                                                              height)
                    distances_to_home.append(dist_to_home)
                    velocity = distance_diff / time_diff
                    speeds.append(velocity * 3.6)
                small_popup_html = "Coordinate: {lat} {lon}<br>" \
                                   "Distance From Home: {dist_to_home:.2f}m<br>" \
                                   "Height: {height:.2f}m<br>" \
                                   "Height From Home: {height_from_home:.2f}m<br>" \
                                   "Velocity: {velocity:.2f}km/h".format(lat=lat,
                                                                         lon=lon,
                                                                         dist_to_home=dist_to_home,
                                                                         height=height,
                                                                         height_from_home=height-home_height,
                                                                         velocity=velocity * 3.6)
                folium.CircleMarker(
                    location=[lat, lon],
                    radius=5,
                    # color=colors[idx % len(colors)],
                    # fill_color=colors[idx % len(colors)],
                    fill=True,
                    fill_opacity=0.7,
                    tooltip=folium.Tooltip(small_popup_html)
                ).add_to(fg)
                prev_row = row

            # Add a line connecting the points
            folium.PolyLine(
                locations=coords,
                # color=colors[idx % len(colors)],
                weight=2,
                opacity=0.7
            ).add_to(fg)

            # Add a Marker for the last Coordinate
            max_speed = avg_speed = max_height = max_dist_home = tot_dist = tot_time = 0
            if speeds:
                max_speed = max(speeds)
                avg_speed = mean(speeds)
            if heights:
                max_height = max(heights)
                max_height_home = max_height-home_height
            if distances_to_home:
                max_dist_home = max(distances_to_home)
            if change_in_distances:
                tot_dist = sum(change_in_distances)
            if change_in_times:
                secs = sum(change_in_times)
                tot_time = timedelta(seconds=secs)
            popup_html = "File Name: {file}<br>" \
                         "Last Coordinate: {coord}<br>" \
                         "Max Speed: {max_speed:.2f}km/h<br>" \
                         "Avg Speed: {avg_speed:.2f}km/h<br>" \
                         "Max Height: {max_height:.2f}m<br>" \
                         "Max Height From Home: {max_height_home:.2f}m<br>" \
                         "Max Distance From Home: {max_dist_home:.2f}m<br>" \
                         "Total Distance Flown: {tot_dist:.2f}m<br>" \
                         "Total Flight Time: {tot_time}".format(file=filename,
                                                                coord=final_coord,
                                                                max_speed=max_speed,
                                                                avg_speed=avg_speed,
                                                                max_height=max_height,
                                                                max_height_home=max_height_home,
                                                                max_dist_home=max_dist_home,
                                                                tot_dist=tot_dist,
                                                                tot_time=tot_time)
            iframe = folium.IFrame(popup_html)
            folium.Marker(
                location=final_coord.split(),
                popup=folium.Popup(iframe,
                                   min_width=350,
                                   max_width=350)
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
