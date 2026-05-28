# -*- coding: utf-8 -*-

"""
Carte interactive du Grand Tour de France (200 étapes)

Installation :
    pip install folium

Utilisation :
    python grand_tour_france.py
"""

import json
import webbrowser
from pathlib import Path

import folium
from folium.plugins import AntPath

# ============================================================
# CHARGEMENT DU JSON
# ============================================================

with open("tour.json", "r", encoding="utf-8") as f:
    data = json.load(f)

tour = data["data"]["tour"]
places = tour["places"]

print(f"\n{len(places)} étapes chargées")

# ============================================================
# CRÉATION DE LA CARTE
# ============================================================

first = places[0]

m = folium.Map(
    location=[first["latitude"], first["longitude"]],
    zoom_start=6,
    tiles="CartoDB positron"
)

coordinates = []

# ============================================================
# AJOUT DES MARQUEURS
# ============================================================

for index, place in enumerate(places, start=1):

    lat = place["latitude"]
    lon = place["longitude"]
    name = place["name"]

    coordinates.append((lat, lon))

    # Couleurs spéciales début / fin
    if index == 1:
        color = "green"
        icon = "play"

    elif index == len(places):
        color = "red"
        icon = "stop"

    else:
        color = "blue"
        icon = "info-sign"

    popup_html = f"""
    <div style="width:260px">
        <h3>Étape {index}</h3>
        <b>{name}</b><br><br>

        Latitude : {lat}<br>
        Longitude : {lon}<br><br>

        ID : {place["id"]}
    </div>
    """

    folium.Marker(
        location=[lat, lon],
        tooltip=f"{index} - {name}",
        popup=folium.Popup(popup_html, max_width=300),
        icon=folium.Icon(color=color, icon=icon)
    ).add_to(m)

# ============================================================
# TRACE DU PARCOURS
# ============================================================

folium.PolyLine(
    coordinates,
    color="blue",
    weight=3,
    opacity=0.7
).add_to(m)

# Ligne animée
AntPath(
    locations=coordinates,
    delay=800,
    color="red",
    pulse_color="white",
    weight=4
).add_to(m)

# ============================================================
# AJUSTEMENT DU ZOOM
# ============================================================

m.fit_bounds(coordinates)

# ============================================================
# INFOS
# ============================================================

distance = tour.get("total_distance", 0)

title_html = f"""
<h3 align="center" style="font-size:20px">
<b>{tour["name"]}</b><br>
Distance totale : {distance:.2f} km<br>
Étapes : {len(places)}
</h3>
"""

m.get_root().html.add_child(folium.Element(title_html))

# ============================================================
# SAUVEGARDE
# ============================================================

output_file = "grand_tour_france.html"

m.save(output_file)

print(f"\nCarte générée : {output_file}")

# Ouverture automatique
webbrowser.open(f"file://{Path(output_file).resolve()}")

print("Carte ouverte dans le navigateur.")
