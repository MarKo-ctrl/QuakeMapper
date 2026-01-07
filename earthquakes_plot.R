library(readr)
library(dplyr)
library(ggplot2)
library(sf)
library(ggspatial)
library(tmap)


setwd('D:\\python\\QuakeMapper')
args <- commandArgs(trailingOnly = TRUE)
print(args[1])
gdf_wm <- st_read(args[1])
# print(gdf_wm)


# earthquakes_gdf <- st_as_sf(
# 	earthquakes,
# 	coords = c("LONG (E)", "LAT (N)"),
# 	crs = 4326
# )

# gdf_wm <- st_transform(earthquakes_gdf, 3857)

#plot <- ggplot(data = gdf_wm)+
#	geom_sf(aes(fill='MAGNITUDE(Local)'))+
#	scale_colour_viridis_d(name='Magnitude')

#print(plot)

tm_shape(gdf_wm) +
	tm_bubbles(size = "MAGNITUDE(Local)", fill = "DEPTH(km)") +
	tm_basemap("CartoDB.Positron")

# group by month
by_month <- gdf_wm %>% group_by(MONTH)
by_month_split <- group_split(by_month)
group_keys(by_month)

# plot each month's earthquakes
common_bbox <- st_bbox(gdf_wm)

testing <- lapply(by_month_split, function(month) {
	tm_shape(month, bbox = common_bbox) +
		tm_bubbles(
			size = "MAGNITUDE(Local)",
			size.legend = tm_legend(title = "Magnitude", position = c("left", "top")),
			size.scale = tm_scale_continuous(ticks = c(1, 2, 3, 4, 5, 6)),
			fill = "DEPTH(km)",
			fill.legend = tm_legend(
				title = "Depth (km)",
				position = c("left", "top")
			),
			fill.scale = tm_scale_intervals(
				values = "-purple_yellow",
				breaks = seq(0, 80, by = 10)
			)
		) +
		tm_title(
			paste0("Earthquakes on ", month$MONTH[[1]], " 2021"),
			size = 1.2,
			frame = TRUE,
			position = tm_pos_in(pos.h = "center")
		)
})

maps <- lapply(by_month_split, function(month) {
	tm_shape(month, bbox = common_bbox) +
		tm_bubbles(size = "MAGNITUDE(Local)", fill = "DEPTH(km)") +
		tm_title(month$MONTH[[1]], size = 1.2) +
		tm_basemap("CartoDB.Positron")
})

# save maps
for (i in seq(1, length(testing))) {
	tmap_save(
		testing[[i]],
		filename = paste0("map_", group_keys(by_month) %>% slice(i), ".png")
	)
}

for (i in seq(1, length(maps))) {
	tmap_save(
		maps[[i]],
		filename = paste0("map_", group_keys(by_month) %>% slice(i), ".png")
	)
}

maps[[1]]
