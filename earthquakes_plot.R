# runtime fallback for missing browser option
if (identical(getOption("browser"), "") || is.null(getOption("browser"))) {
  xb <- Sys.which("xdg-open")
  if (nzchar(xb)) {
    options(browser = xb)
  } else {
    Sys.setenv(BROWSER = "/usr/bin/firefox") # adjust to installed browser if needed
  }
}

library(readr)
library(dplyr)
library(ggplot2)
library(sf)
library(ggspatial)
library(tmap)
library(stars)


# windows
# setwd('D:\\python\\QuakeMapper')
#linux
setwd('/home/marko/PROJECTS/QuakeMapper')

# file = '.\\Data\\heraklion_positron.tif'
file = 'Data/heraklion_positron.tif'
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
			size.scale = tm_scale_continuous(values.scale = 2, 
				ticks = c(1, 2, 3, 4, 5, 6)),
			fill = "Depth.km.",
			fill.legend = tm_legend(
				title = "Depth (km)",
				position = c("left", "top")
			),
			fill.scale = tm_scale_intervals(
				values = "brwn_yl",
				value.na = "#C1C1C1",
				breaks = seq(0, 80, by = 20)
			)
		) +
		tm_title(
			paste0("Earthquakes on ", month$Month[[1]], " 2021"),
			size = 1.2,
			frame = TRUE,
			position = tm_pos_in(pos.h = "center")
		)
})

# save maps (optional — keep if you still want individual PNGs)
# for (i in seq(1, length(maps))) {
# 	tmap_save(
# 		maps[[i]],
# 		filename = paste0("map_", group_keys(by_month) %>% slice(i), ".png")
# 	)
# }

seconds_per_frame <- if (length(args) >= 2 && nzchar(args[2])) as.numeric(args[2]) else 2
if (is.na(seconds_per_frame) || seconds_per_frame <= 0) seconds_per_frame <- 2
anim_file <- if (length(args) >= 3 && nzchar(args[3])) args[3] else "earthquakes_monthly.gif"

# export frames to temp dir
tmp_dir <- tempfile("maps_")
dir.create(tmp_dir)
png_files <- vapply(seq_along(maps), function(i) {
  f <- file.path(tmp_dir, sprintf("frame_%02d.png", i))
  tmap_save(maps[[i]], filename = f, width = 1400, height = 900)
  f
}, FUN.VALUE = character(1))

# use magick (preferred) or gifski; both allow setting frame durations precisely
if (requireNamespace("magick", quietly = TRUE)) {
  imgs <- magick::image_read(png_files)
  animated <- magick::image_animate(imgs, delay = as.integer(seconds_per_frame * 100))
  magick::image_write(animated, anim_file)
  message("Saved animation to ", anim_file, " (magick, ", seconds_per_frame, " s/frame)")
} else {
  # fallback: duplicate frames to approximate duration and use tmap_animation
  rep_factor <- max(1, round(seconds_per_frame))
  maps_slow <- rep(maps, each = rep_factor)
  tmap_animation(maps_slow, filename = anim_file, width = 1400, height = 900, fps = 1)
  message("Saved animation to ", anim_file, " (fallback approx ", seconds_per_frame, " s/frame)")
}


# Create an animated GIF from the monthly maps using tmap_animation
# if (!requireNamespace("magick", quietly = TRUE) && !requireNamespace("gifski", quietly = TRUE)) {
#   message("Install 'magick' or 'gifski' to enable GIF export: install.packages('magick') or install.packages('gifski')")
# } else {
#   anim_file <- "earthquakes_monthly.gif"
#   # fps = frames per second (1 gives one month per second)
#   #tmap_animation(maps, filename = anim_file, width = 1400, height = 900, fps = 1)
#   maps_slow <- rep(maps, each = 3) # repeat each map 3 times to slow down the animation
#   tmap_animation(maps_slow, filename = anim_file, width = 1400, height = 900, fps = 1)
#   message("Saved animation to ", anim_file)
# }

# Alternatively, you can build a single tm object and animate facets:
# tm_obj <- tm_shape(basemap) +
#   tm_rgb() +
#   tm_shape(gdf_wm, bbox = common_bbox) +
#   tm_bubbles(
#     size = "Magnitude.Local.",
#     fill = "Depth.km.",
#     size.scale = tm_scale_continuous(ticks = c(1,2,3,4,5,6)),
#     fill.scale = tm_scale_intervals(values = "brwn_yl", breaks = seq(0,80,by=20))
#   ) +
#   tm_facets(along = "Month", free.coords = FALSE)
# tmap_animation(tm_obj, filename = "earthquakes_months_facets.gif", fps = 1)


