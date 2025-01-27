# Bus_Routes

## Dictionary

| **key**           | **desc**                                                                                                                                                                      | **example**                                                                                            |
|-------------------|-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|--------------------------------------------------------------------------------------------------------|
| **Route_Numb**    | The numerical identifier assigned to the route.                                                                                                                               | "Route 22", "Route 210", "City Link Green"                                                             |
| **Route_Name**    | The name of the public transportation route, such as a bus or rail route, that serves a specific geographic area.                                                             | "BALTIMORE - ANNAPOLIS"                                                                                |
| **Route_Type**    | Refers to the type of public transportation service the route represents.                                                                                                     | MTA Commuter Bus, MTA Local Bus - Express BusLink, MTA Local Bus - LocalLink, MTA Local Bus - CityLink |
| **Shape__Length** | Refers to the length of the route or road segment in GIS (Geographic Information System) in internal units. This data helps provide the physical extent of the route.         | A numeric value between 0.02 and 0.5                                                                   |
| ~~Distribute~~    | Likely refers to the distribution of ridership data or traffic data, which could include how ridership is distributed across different times, days, or segments of the route. | "E1 - Public Domain - Internal Use Only"                                                               |

## Example

| Route_Name                        | Route_Type       | Route_Numb | Distributi                             | Shape__Length |
|-----------------------------------|------------------|------------|----------------------------------------|---------------|
| KENT ISLAND - ANNAPOLIS/BALTIMORE | MTA Commuter Bus | 210        | E1 - Public Domain - Internal Use Only | 0.243663477   |
| BALTIMORE - ANNAPOLIS             | MTA Commuter Bus | 215        | E1 - Public Domain - Internal Use Only | 0.244740073   |
| COLUMBIA - BALTIMORE              | MTA Commuter Bus | 310        | E1 - Public Domain - Internal Use Only | 0.243663477   |
| LAUREL - BALTIMORE                | MTA Commuter Bus | 320        | E1 - Public Domain - Internal Use Only | 0.21182485    |
| CHURCHVILLE - BALTIMORE           | MTA Commuter Bus | 410        | E1 - Public Domain - Internal Use Only | 0.38804184    |
| HICKORY - HOPKINS HOSPITAL        | MTA Commuter Bus | 411        | E1 - Public Domain - Internal Use Only | 0.400822012   |
