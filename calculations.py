import math


def distance_calc(lat1, lon1, height1, lat2, lon2, height2):
    earth_radius = 6371000  # approximately 6,371 km

    # Convert degrees to radians
    lat1, lon1, lat2, lon2 = map(math.radians, [lat1, lon1, lat2, lon2])

    # Haversine formula
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = math.sin(dlat / 2) ** 2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2) ** 2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    distance = earth_radius * c

    # Calculate the height difference
    height_diff = abs(height1 - height2)

    # Add the height difference to the distance
    distance_with_height = math.sqrt(distance ** 2 + height_diff ** 2)

    return distance_with_height
