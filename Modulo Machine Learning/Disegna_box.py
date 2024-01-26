import folium


def draw_bbox_on_map(bbox):

    if bbox:
        # Calcola il centro del bounding box
        center_lat = (bbox[1] + bbox[3]) / 2
        center_lon = (bbox[0] + bbox[2]) / 2

        # Crea la mappa centrata sul bounding box
        map_object = folium.Map(location=[center_lat, center_lon], zoom_start=10)

        # Aggiungi il bounding box come rettangolo alla mappa
        folium.Rectangle(
            bounds=[[bbox[3], bbox[2]], [bbox[1], bbox[0]]],
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
