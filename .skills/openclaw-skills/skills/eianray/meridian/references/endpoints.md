# Meridian Endpoints — Full Reference

All paid endpoints require `X-PAYMENT` header on retry. All accept multipart/form-data.

## Info (free)
| Endpoint | Method | Description |
|----------|--------|-------------|
| `/v1/health` | GET | Health check — returns status, version, request_id |

## Schema / Validation (paid)
| Endpoint | Params | Description |
|----------|--------|-------------|
| `/v1/schema` | `file` | Field names, types, CRS, geometry type, feature count, bbox |
| `/v1/validate` | `file` | Geometry validity report |
| `/v1/repair` | `file` | Fix invalid geometries |

## Format Conversion (paid)
| Endpoint | Params | Description |
|----------|--------|-------------|
| `/v1/convert` | `file`, `output_format` | GeoJSON → geojson/shapefile/kml/gpkg |

## Core GIS (paid)
| Endpoint | Params | Description |
|----------|--------|-------------|
| `/v1/reproject` | `file`, `target_crs`, `source_crs`(opt) | Reproject to any GDAL CRS string |
| `/v1/buffer` | `file`, `distance` (meters) | Buffer features (auto-UTM projection) |
| `/v1/clip` | `file`, `mask` | Clip to polygon mask |
| `/v1/dissolve` | `file`, `field_name`(opt) | Merge features by attribute |

## Geometry Transforms (paid)
| Endpoint | Params | Description |
|----------|--------|-------------|
| `/v1/erase` | `file` | Delete all features, preserve schema |
| `/v1/feature-to-point` | `file` | Convert geometries to centroid points |
| `/v1/feature-to-line` | `file` | Extract polygon boundaries as LineStrings |
| `/v1/feature-to-polygon` | `file` | Polygonize closed LineStrings |
| `/v1/multipart-to-singlepart` | `file` | Explode multipart geometries |
| `/v1/add-field` | `file`, `field_name`, `field_type`, `default_value`(opt) | Add attribute column |

## Topology — Two-input (paid)
| Endpoint | Params | Description |
|----------|--------|-------------|
| `/v1/union` | `file`, `file_b` | Combine all features from two layers |
| `/v1/intersect` | `file`, `file_b` | Spatial intersection |
| `/v1/difference` | `file`, `file_b` | layer_a minus (layer_a ∩ layer_b) |

## Combine — Two-input (paid)
| Endpoint | Params | Description |
|----------|--------|-------------|
| `/v1/append` | `file`, `file_b` | Add features from file_b into file_a schema |
| `/v1/merge` | `file`, `file_b` | Combine preserving all fields from both |
| `/v1/spatial-join` | `file`, `file_b`, `predicate`(opt) | Join attributes by spatial relationship |

## Vector Tiles (paid)
| Endpoint | Params | Description |
|----------|--------|-------------|
| `/v1/vectorize` | `file`, `layer_name`(opt), `min_zoom`(opt), `max_zoom`(opt) | Generate .mbtiles via tippecanoe |

## DEM / Raster (paid)
| Endpoint | Params | Description |
|----------|--------|-------------|
| `/v1/hillshade` | `file` (GeoTIFF) | Shaded relief |
| `/v1/slope` | `file` (GeoTIFF) | Terrain slope |
| `/v1/aspect` | `file` (GeoTIFF) | Terrain aspect |
| `/v1/roughness` | `file` (GeoTIFF) | Terrain roughness |
| `/v1/color-relief` | `file`, `color_table` | Hypsometric tinting |
| `/v1/contours` | `file`, `interval` | Contour lines (GeoJSON output) |
| `/v1/raster-calc` | `file`, `expression`, additional raster slots | Pixel math via gdal_calc |

## Batch (paid)
| Endpoint | Params | Description |
|----------|--------|-------------|
| `/v1/batch` | `operations` (JSON array, max 50) | Run multiple ops with single payment |
