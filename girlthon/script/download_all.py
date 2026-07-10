from download_osm import download_feature

datasets = {

    "police": {
        "amenity": "police"
    },

    "hospitals": {
        "amenity": "hospital"
    },

    "bus_stops": {
        "highway": "bus_stop"
    },

    "parks": {
        "leisure": "park"
    },

    "schools": {
        "amenity": "school"
    },

    "colleges": {
        "amenity": "college"
    },

    "universities": {
        "amenity": "university"
    },

    "restaurants": {
        "amenity": "restaurant"
    },

    "cafes": {
        "amenity": "cafe"
    },

    "banks": {
        "amenity": "bank"
    },

    "pharmacies": {
        "amenity": "pharmacy"
    },

    "fire_stations": {
        "amenity": "fire_station"
    },

    "fuel": {
        "amenity": "fuel"
    },

    "parking": {
        "amenity": "parking"
    },

    "markets": {
        "shop": "supermarket"
    },

    "malls": {
        "shop": "mall"
    },

    "railway": {
        "railway": "station"
    },

    "metro": {
        "railway": "subway_entrance"
    }

}

for name, tags in datasets.items():
    download_feature(name, tags)

print("\nAll downloads complete!")