from lib import get_data

# t = db_queries.table_exists_complete("polygon_plate_boundaries")
# print(t)
get_data.geojson_to_postgis("data/PB2002_plates.json", "polygon_plate_boundaries")