import geopy.distance as gpd
from datetime import datetime, timedelta
import boto3
import json

def set_coordinates(event):

    # Define the initial variables
    central_coordinate = (event["latitude"], event["longitude"])
    radius = float(event["radius"])
    number_of_points = int(event["points"])

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
    print(distance_to_add)

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

    number_of_points = int(event["points"])
    days = int(event["days"])

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

def create_schedule_rule(events_client, evt, radius):
    # Setting variables
    schedule_time = evt[0].replace(
        " ", ""
        ).replace(
            ":", "", 2
            ).replace(
                "-", "", 2
                )
    rule_name = "nearby_rule"+str(schedule_time)
    region = "sa-east-1"
    acc_id = "820949372807"
    function_name = "data-cloud-project-maps-nearby"
    function_arn = f"arn:aws:lambda:{region}:{acc_id}:function:{function_name}"
    datetime_object = datetime.strptime(evt[0], '%Y-%m-%d %H:%M:%S')
    minutes = str(datetime_object.minute).zfill(2)
    hour = str(datetime_object.hour).zfill(2)
    day = str(datetime_object.day).zfill(2)
    month = str(datetime_object.month).zfill(2)
    year = str(datetime_object.year)
    cron_expression = f"at({year}-{month}-{day}T{hour}:{minutes}:00)"
    event_for_nearby = {
        "coordinate": evt[1],
        "radius": radius
    }
    print(schedule_time, rule_name, cron_expression)

    # Create the rule with a one-time schedule
    role_name = "data-cloud-project-maps-nearby-role-r57024ap"
    response = events_client.create_schedule(
        Name=rule_name,
        ScheduleExpression=cron_expression,
        State='ENABLED',
        ScheduleExpressionTimezone="Europe/Brussels",
        FlexibleTimeWindow={
            'Mode': 'OFF'
        },
        Target={
            "Arn": function_arn,
            "Input": event_for_nearby,
            "RoleArn": f"arn:aws:iam::{acc_id}:role/service-role/{role_name}"
        }
    )
    return response

def lambda_handler(event, context):
    radius = float(event["radius"])
    event_bridge_client = boto3.client('scheduler')
    coordinates = set_coordinates(event)
    distributed_events_for_nearby = create_events_month(event, coordinates)

    # create rule in event bridge for each coordinate
    for evt in distributed_events_for_nearby:
        print("Creating rule:", evt)
        response = create_schedule_rule(
            event_bridge_client, 
            evt,
            radius)
        print("Schedule Arn:", response)