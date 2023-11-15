# BikeMi Data and Simulation

## BikeMi Overview
- Average distance per ride: 2.3 km
- Average duration per ride: 11.5 minutes
- Average electric scooter range: 20-30 km per charge
- Service operates 365 days a year from 6:00 AM to 12:00 AM
- BikeMi has 325 stations with 5430 bicycles (4280 classic, 1000 e-bikes, 150 pedal-assisted with child seat)
- [BikeMi Website](https://bikemi.com/)

## Real-time Data
- [Real-time BikeMi Data](https://bikemi.com/dati-aperti/tempo-reale)

## Usage Statistics
- Peak usage between 16:00 and 20:00
- [Article on Electric Scooters](https://www.brindisioggi.it/monopattini-elettrici-in-due-settimane-percorsi-7mila-chilometri-una-tonnellata-in-meno-di-co2/): 7,000 km covered in two weeks, reducing CO2 emissions
- [Milano Corriere Article](https://milano.corriere.it/notizie/cronaca/23_marzo_30/bici-elettriche-in-sharing-a-milano-istruzioni-per-l-uso-prezzi-sconti-app-parcheggi-e-optional-7ac31d5c-1dc5-49af-a353-f8eabe758xlk.shtml): 9,000 shared bikes, five operators, 15,000 rentals per day

## Simulation Parameters
- Daily unlocks: 7500
- Average distance per ride: 2.3 km
- Average duration per ride: 11.5 minutes
- Battery autonomy: 20 km
- Stations: 324 (18x18 grid, 750m distance)
- Station capacity: 15 bikes, max 22 bikes
- Daily rentals distributed: 40% during 16:00-20:00, 60% evenly distributed
- Simulation duration: 18 hours (6:00-24:00), 1080 minutes

## Simulation Calculations
- Space unit: 750 meters
- Time unit: 1 minute
- Consumption per space unit: 37.5 (750m / 20km * 1000)
- Speed: 15 km/h -> 0.33 space/minute
- Rental space: 3.06 (2.3 km / 0.75)

## Rental Distribution
- Peak hours (16:00-20:00): 40% of daily rentals
- Non-peak hours evenly distributed
- Peak hour rentals: 3000, subtract 1285 evenly distributed to simulate Gaussian distribution

## Modeling Distances and Speeds
- Distance modeled with a normal distribution (mean: 3.06, std: 0.5)
- Speed modeled with a normal distribution (mean: 0.33, std: 0.05)

## Charging Station Power
- Unknown charging time (x)
- Station power: 1000/x
- Example: x = 10 minutes -> Station power: 1000/10 = 100