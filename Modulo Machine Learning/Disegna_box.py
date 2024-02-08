import folium


def draw_bbox_on_map(bbox):

    min_lat, min_lon, max_lat, max_lon = bbox  # bbox tipo overpass

    if bbox:
        # Calcola il centro del bounding box
        center_lat = (min_lat + max_lat) / 2
        center_lon = (min_lon + max_lon) / 2

        # Crea la mappa centrata sul bounding box
        map_object = folium.Map(location=[center_lat, center_lon], zoom_start=10)

        # Aggiungi il bounding box come rettangolo alla mappa
        folium.Rectangle(
            bounds=[[max_lat, max_lon], [min_lat, min_lon]],
            color='blue',
            fill=True,
            fill_color='blue',
            fill_opacity=0.2
        ).add_to(map_object)

        # Salva la mappa su un file HTML
        map_filename = f'map_with_bbox.html'
        map_object.save(map_filename)
        print(f"Bounding box salvato in: {map_filename}")
        return True
    else:
        print(f"Bounding box non disponibile.")
        return False


"""
# Esempio di utilizzo
bbox_example = (40.6115, 40.6259, 14.3611, 14.3886)
draw_bbox_on_map(bbox_example)
"""

# draw_bbox_on_map("Sorrento", "here")
