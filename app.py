import geopy.distance as gpd
import datetime
import boto3
import json

def lambda_handler(event, context):

    # Define the initial variables
    coordinate = (event["latitude"], event["longitude"])
    radius = event["radius"]
    number_of_points = event["points"]
    days = event["days"]


    angles = [315, 225, 135, 45]
    v = 1 # round
    p = 1 # point
    pv = 1 # point in round

    # list that will contain all the coordinates
    coordinates = []

    # including the center coordinate
    coordinates.append(coordinate)

    # setting the first coordinate
    distance_to_add = gpd.distance(meters=(2*radius))
    coordinate = distance_to_add.destination(coordinate, bearing=90)
    coordinates.append((coordinate.latitude, coordinate.longitude))

    while p<number_of_points:
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
            coordinate = distance_to_add.destination(
                coordinate_,
                bearing=angle
                )
            coordinates.append((coordinate.latitude, coordinate.longitude))
        else:
            distance_to_add = gpd.distance(meters=(radius*(2**0.5)))
            # iterate along the angle array (used in bearing arg)
            for angle in angles:
                # amount of coordinate for each angle
                for _ in range(2*v):
                    p += 1
                    pv += 1
                    # Add the coordinates to the list
                    coordinate_ = coordinate
                    coordinate = distance_to_add.destination(
                        coordinate_, 
                        bearing=angle
                        )
                    coordinates.append(
                        (coordinate.latitude, coordinate.longitude)
                        )
                    if p == number_of_points or pv == 8*v:
                        break
                if p == number_of_points or pv == 8*v:
                    break
            if p == number_of_points:
                break

    # distribute all the event along the days
    minutes_in_given_days = days*24*60
    fixed_interval = (minutes_in_given_days/number_of_points).__floor__()
    current_datetime = datetime.datetime.now()
    events_datetime = [
        (
        current_datetime + datetime.timedelta(
        minutes=(point*fixed_interval)
        )
        ) 
        for point in range(1, number_of_points+1)
        ]
    events_to_nearby = [
        (event_datetime.strftime('%Y-%m-%d %H:%M:%S'), coordinate)
        for event_datetime, coordinate in zip(events_datetime, coordinates)
        ]

    # send the events to EventBridge and then to the nearby lambda
    event_bridge_client = boto3.client('events')

    # Convert the event data to JSON
    event_data_json = json.dumps(events_to_nearby)

    for event in event_data_json:
        # Define the parameters for the PutEvents operation
        put_events_params = {
            'Entries': [
                {
                    'Source': context.function_name,
                    'Target': "data-cloud-project-gmaps-nearby",
                    'Detail': event
                }
            ]
        }
        # Send the event to EventBridge
        response = event_bridge_client.put_events(**put_events_params)