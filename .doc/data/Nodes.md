# nodes_all & nodes_drive

## Directory

| **key**      | **type**        | **desc**                                                                                                                                                                | **example**                                                                 |
|--------------|-----------------|-------------------------------------------------------------------------------------------------------------------------------------------------------------------------|-----------------------------------------------------------------------------|
| **osmid**    | `int`           | The unique identifier for an element in OpenStreetMap (OSM). This represents a node.                                                                                    | Numeric value                                                               |
| **y**        | `float`         | The latitude coordinate of a point (node) in the OSM dataset. Used for geographic positioning.                                                                          | A numeric value between 39 and 40                                           |
| **x**        | `float`         | The longitude coordinate of a point (node) in the OSM dataset. Also used for geographic positioning.                                                                    | A numeric value between -77 and -76                                         |
| **geometry** | `Point`         | A spatial representation of a line or area, often stored in formats like WKT (Well-Known Text). It describes the shape or path of a feature such as a road or boundary. | For example, nodes are all points on a map.                                 |
| street_count | `int`           | The number of streets (or ways) connected to a particular node. It can indicate intersections or endpoints.                                                             | An integer between 1 and 15                                                 |
| highway      | `str`           | Indicates the type of road or path.                                                                                                                                     | It can represent values like residential, primary, secondary, footway, etc. |
| ref          | `str`           | A reference code for the road, path, or other infrastructure.                                                                                                           | This might correspond to road numbers (e.g., "I-80" for an interstate).     |
| railway      | `Optional[str]` | Specifies if the node or way is part of a railway.                                                                                                                      | For example, level crossing or subway entrance.                             |
| junction     | `Optional[str]` | Represents information about a junction, such as its type.                                                                                                              | For example, a roundabout.                                                  |


## Examples

|  osmid   | y          | x           | highway           | ref | street_count | junction | railway | geometry                       |
|:--------:|------------|-------------|-------------------|-----|--------------|----------|---------|--------------------------------|
| 27029857 | 39.2316281 | -76.5076714 | motorway_junction | 44  | 3            |          |         | POINT (-76.5076714 39.2316281) |
| 37018071 | 39.3868849 | -76.525801  |                   |     | 1            |          |         | POINT (-76.525801 39.3868849)  |
| 37018073 | 39.3875934 | -76.5251871 |                   |     | 3            |          |         | POINT (-76.5251871 39.3875934) |
| 37018082 | 39.2970522 | -76.4221001 |                   |     | 1            |          |         | POINT (-76.4221001 39.2970522) |
| 37018098 | 39.2976881 | -76.421585  |                   |     | 3            |          |         | POINT (-76.421585 39.2976881)  |
| 37018099 | 39.298376  | -76.4208216 |                   |     | 1            |          |         | POINT (-76.4208216 39.298376)  |
| 37018114 | 39.317318  | -76.45271   |                   |     | 3            |          |         | POINT (-76.45271 39.317318)    |
| 37018165 | 39.3147418 | -76.4537907 |                   |     | 1            |          |         | POINT (-76.4537907 39.3147418) |
| 37018175 | 39.4715402 | -76.6071263 |                   |     | 4            |          |         | POINT (-76.6071263 39.4715402) |
| 37018198 | 39.4694733 | -76.6083103 |                   |     | 1            |          |         | POINT (-76.6083103 39.4694733) |
| 37018232 | 39.2381077 | -76.4501839 |                   |     | 4            |          |         | POINT (-76.4501839 39.2381077) |
| 37018237 | 39.23978   | -76.4487102 |                   |     | 4            |          |         | POINT (-76.4487102 39.23978)   |
| 37018241 | 39.2413432 | -76.4473472 |                   |     | 3            |          |         | POINT (-76.4473472 39.2413432) |
| 37018248 | 39.2712983 | -76.5273321 |                   |     | 3            |          |         | POINT (-76.5273321 39.2712983) |
| 37018250 | 39.271315  | -76.529156  |                   |     | 3            |          |         | POINT (-76.529156 39.271315)   |
| 37018259 | 39.3388712 | -76.4106681 |                   |     | 3            |          |         | POINT (-76.4106681 39.3388712) |
| 37018301 | 39.3825851 | -76.5086917 |                   |     | 3            |          |         | POINT (-76.5086917 39.3825851) |
| 37018303 | 39.3821998 | -76.5089568 |                   |     | 3            |          |         | POINT (-76.5089568 39.3821998) |
| 37018307 | 39.3815781 | -76.5093846 |                   |     | 1            |          |         | POINT (-76.5093846 39.3815781) |
| 37018334 | 39.4599628 | -76.7778402 |                   |     | 3            |          |         | POINT (-76.7778402 39.4599628) |
| 37018353 | 39.4608145 | -76.7771044 |                   |     | 3            |          |         | POINT (-76.7771044 39.4608145) |
| 37018435 | 39.4593806 | -76.776164  |                   |     | 3            |          |         | POINT (-76.776164 39.4593806)  |
| 37018475 | 39.4574617 | -76.7783588 |                   |     | 4            |          |         | POINT (-76.7783588 39.4574617) |
| 37018533 | 39.4548666 | -76.7796742 |                   |     | 3            |          |         | POINT (-76.7796742 39.4548666) |
| 37018552 | 39.454849  | -76.7811247 |                   |     | 3            |          |         | POINT (-76.7811247 39.454849)  |
| 37018562 | 39.33519   | -76.461802  |                   |     | 3            |          |         | POINT (-76.461802 39.33519)    |
| 37018563 | 39.3356453 | -76.4628244 | turning_circle    |     | 1            |          |         | POINT (-76.4628244 39.3356453) |
| 37018567 | 39.492619  | -76.543969  |                   |     | 3            |          |         | POINT (-76.543969 39.492619)   |
