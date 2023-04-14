import geopy.distance as gpd
# Define the center coordinate
coordinate = (40.7128, -74.0060)

# Define the distance between points in meters
radius = 200 # 200 meter
points = 50
# Generate pairs of coordinates
coordinates = []
angles = [315, 225, 135, 45]
v = 1 # round
p = 1 # point
pv = 1 # point in round

# including the center coordinate
coordinates.append(coordinate)

# setting the first coordinate
distance_to_add = gpd.distance(meters=(2*radius))
coordinate = distance_to_add.destination(coordinate, bearing=90)
coordinates.append((coordinate.latitude, coordinate.longitude))


while p<points:
    print(p, pv, v)
    # check if is the last point of the round
    if pv == 8*v:
        p += 1
        pv = 1
        v += 1
        # set the first coordinate of the round
        distance = radius * (10**0.5)
        angle = 71.565
        distance_to_add = gpd.distance(meters=distance)
        coordinate_ = coordinate
        coordinate = distance_to_add.destination(coordinate_, bearing=angle)
        coordinates.append((coordinate.latitude, coordinate.longitude))
    else:
        distance_to_add = gpd.distance(meters=(radius*(2**0.5)))
        # iterate along the angle array (used in bearing arg)
        for angle in angles:
            # amount of coordinate for each angle
            for i in range(2*v):
                print(p, pv, v)
                p += 1
                pv += 1
                # Add the coordinates to the list
                coordinate_ = coordinate
                coordinate = distance_to_add.destination(coordinate_, bearing=angle)
                coordinates.append((coordinate.latitude, coordinate.longitude))
                if p == points or pv == 8*v:
                    break
            if p == points or pv == 8*v:
                break
        if p == points:
            break