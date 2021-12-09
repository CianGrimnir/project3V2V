# CS7NS1 Scalable Computing Project 3: V2V Network

Group 17
- Azin Makaranth
- Omkar Pramod Padir
- Rakesh N

# Overview

Multiple vehicle instances (`vehicle.py`) will be running on each pi with 'n' numbers
of coupled sensors defined under (`sensor_data_generators.py`). Each sensor type is 
associated with a range of possible values and broadcast to the neighbouring vehicles
via sockets. The following sensor types with corresponding ranges as defined:
- `pressure` (PSI) : [0, 100]
- `speed` (km/h) : [40, 80]
- `light` : ['day', 'night']
- `Fuel` (%) : [40, 80]
- `Proximity` (position) : [left, right, front, behind] 
- `Brake` : [0, 4]
- `heartrate` (BPM) : [40, 120]
- `GPS` (gps coordinates) : latitude - [-90, 90], longitude - [-180, 180]
- `proximity` (m) : [1, 50]

Each Pi can additionally run a single infrastructure instance (`vehicle.py --node_type=i`)
which acts as both a peer (via sockets) to other vehicles. At minimum, conformant endpoints
serve a JSON object with speed, wiper speed, tyre pressure and fuel data, as well as a list
of other known peers. 


# Dependencies

All the nodes are implemented in Python 3. Vehicle and sensors nodes uses the 
standard library,[Flask](https://flask.palletsprojects.com/) for providing 
external API, [geopy](https://geopy.readthedocs.io/) package is used to calculate
the distance between two nodes/vehicles/infra, [pycryptodome](https://pycryptodome.readthedocs.io/)
is used for adding encryption to the sending data.

# Installation

```sh
$ pip3 install -r requirements.txt
```
Following packages will be installed -
```sh
$ Packages to be installed -
    geopy
    flask
    pycryptodome
```

# Running Simulation
```sh
# For running a vehicle node
$ python3 vehicle.py --listen_port 33535 --sending_port 34535 --vehicle_id 4 --latitude 53.37527718212891 --longitude -6.285589418171051 --api_port 5001
# For running a Infra node
$ python3 vehicle.py --node_type i --listen_port 33555 --sending_port 34555 --vehicle_id 2 --latitude 53.375099182128906 --longitude -6.285900115966797 --api_port 5000 
```