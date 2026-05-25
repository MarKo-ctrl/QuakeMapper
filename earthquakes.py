# import pprint
# from datetime import date
# from lib import get_data
from lib import db_queries

# get_data.fetch_all(2000, 2003)
# get_data.fetch_all(2003, 2005)
# get_data.fetch_all(2005, 2010)
# get_data.fetch_all(2010, 2026)

# eq_2010_2011 = transform.load_by_year_range(2010, 2011)
# print(eq_2010_2011.head(10))

eq_45_5 = db_queries.load_magnitude_range(4.5, 5.1)
print(eq_45_5.head(10))

cal_eq = db_queries.load_by_bbox(*(-125.222168,30.845647,-113.884277,39.487085))
print(cal_eq.shape)