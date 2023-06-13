import geopy.distance as gpd
from datetime import datetime, timedelta
import boto3
import json

def set_coordinates(event):

    # Define the initial variables
    central_coordinate = (event["latitude"], event["longitude"])
    radius = event["radius"]
    number_of_points = event["points"]

    # Initial variables for iteration that setup all coordinates
    angles = [315, 225, 135, 45]
    turn = 1
    point = 1
    point_in_turn = 1

    # list that will contain all coordinates, including the center coordinate
    coordinates = [central_coordinate]

    # setting the first coordinate
    distance_to_add = gpd.distance(meters=(2*radius))
    coordinate = distance_to_add.destination(central_coordinate, bearing=90)
    coordinates.append((coordinate.latitude, coordinate.longitude))

    while point<number_of_points:
        print(point, point_in_turn, turn)
        # check if it's the last point of the turn
        if point_in_turn == 8*turn:
            point += 1
            point_in_turn = 1
            turn += 1
            # set the first coordinate of the turn
            distance = radius * (10**0.5)
            angle = 71.565
            distance_to_add = gpd.distance(meters=distance)
            previous_coordinate = coordinate
            coordinate = distance_to_add.destination(
                previous_coordinate,
                bearing=angle
                )
            coordinates.append((coordinate.latitude, coordinate.longitude))
        else:
            distance_to_add = gpd.distance(meters=(radius*(2**0.5)))
            # iterate along the angle array (used in bearing arg)
            for angle in angles:
                # amount of coordinate for each angle
                for _ in range(2*turn):
                    point += 1
                    point_in_turn += 1
                    # Add the coordinates to the list
                    previous_coordinate = coordinate
                    coordinate = distance_to_add.destination(
                        previous_coordinate, 
                        bearing=angle
                        )
                    coordinates.append(
                        (coordinate.latitude, coordinate.longitude)
                        )
                    if point == number_of_points or point_in_turn == 8*turn:
                        break
                if point == number_of_points or point_in_turn == 8*turn:
                    break
            if point == number_of_points:
                break

    return coordinates

def create_events_month(event, coordinates):

    number_of_points = event["points"]
    days = event["days"]

    # distribute all the event along the days
    minutes_in_given_days = days*24*60
    fixed_interval = (minutes_in_given_days/number_of_points).__floor__()
    current_datetime = datetime.now()
    events_datetime = [
        (
        current_datetime + timedelta(
        minutes=(point*fixed_interval)
        )
        ) 
        for point in range(1, number_of_points+1)
        ]
    distributed_events_for_nearby = [
        [event_datetime.strftime('%Y-%m-%d %H:%M:%S'), coordinate]
        for event_datetime, coordinate in zip(events_datetime, coordinates)
        ]
    
    return distributed_events_for_nearby

def lambda_handler(event, context):

    coordinates = set_coordinates(event)
    distributed_events_for_nearby = create_events_month(event, coordinates)

    # send the events to EventBridge and then to the nearby lambda
    event_bridge_client = boto3.client('events')

    for evt in distributed_events_for_nearby:
        # Include the evt (datetime and coordinate)
        event_for_nearby = {
            'timestamp': evt[0],
            'coordinate': evt[1]
        }
        # Define the parameters for the PutEvents operation
        put_events_params = {
            'Entries': [
                    {
                    'Source': context.function_name,
                    'Target': "data-cloud-project-gmaps-nearby",
                    'Time': evt[0],
                    'Detail': json.dumps(event_for_nearby)
                }
            ]
        }
        # Send the event to EventBridge
        response = event_bridge_client.put_events(**put_events_params)
        print(response)