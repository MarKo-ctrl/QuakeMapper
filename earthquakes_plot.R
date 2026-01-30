library(readr)
library(dplyr)
library(ggplot2)
library(sf)
library(ggspatial)
library(tmap)
library(stars)


setwd('D:\\python\\QuakeMapper')

file = '.\\Data\\heraklion_positron.tif'
basemap = stars::read_stars(file)

args <- commandArgs(trailingOnly = TRUE)
gdf_wm <- st_read(args[1])
print(head(gdf_wm))

# group by month
by_month <- gdf_wm %>% group_by(Month)
by_month_split <- group_split(by_month)
group_keys(by_month)

# plot each month's earthquakes
common_bbox <- st_bbox(gdf_wm)

maps <- lapply(by_month_split, function(month) {
	tm_shape(basemap) +
		tm_rgb() +
		tm_shape(month, bbox = common_bbox) +
		tm_bubbles(
			size = "Magnitude.Local.",
			size.legend = tm_legend(title = "Magnitude", position = c("left", "top")),
			size.scale = tm_scale_continuous(ticks = c(1, 2, 3, 4, 5, 6)),
			fill = "Depth.km.",
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
			paste0("Earthquakes on ", month$Month[[1]], " 2021"),
			size = 1.2,
			frame = TRUE,
			position = tm_pos_in(pos.h = "center")
		)
})

# save maps
for (i in seq(1, length(maps))) {
	tmap_save(
		maps[[i]],
		filename = paste0("map_", group_keys(by_month) %>% slice(i), ".png")
	)
}