import sqlalchemy

# from lib import get_data
from lib.db import get_engine
from lib.db_setup import add_table_column

# t = db_queries.table_exists_complete("polygon_plate_boundaries")
# print(t)
# get_data.geojson_to_postgis("data/PB2002_plates.json", "polygon_plate_boundaries")

add_table_column("earthquakes", "plate_name", "TEXT")

engine = get_engine()

with engine.connect() as conn:
    conn.execute(
        sqlalchemy.text("""
                        UPDATE earthquakes eq
                        SET plate_name = pp."PlateName"
                        FROM polygon_plate_boundaries pp
                        WHERE ST_Intersects(eq.geom, pp.geom);
                        """
                        )
                    )
    conn.commit()