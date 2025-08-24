import copy
import math
import random
import numpy
import heapq
import time
import itertools
import collections

file_name = 'Result/15/C101_1-15.csv'
file_name_csv = 'Result/result.csv'
# file_path = "test_data\\Mine\\20x20_15.dat"
# file_path = "test_data\\Smith\\TSPrd(time)\\Solomon\\10\\C101_0.5.dat"
file_path = "test_data//MTVRPRDDR//Instances//U_10_0.5_Num_2.txt"
# file_path = "test_data\\Smith\\TSPrd(time)\\Solomon\\50\\0_5TSP_50\\C101_0.5.dat"
# file_path = "test_data\\data_demand_random\\Solomon\\10\\C101_2.5.dat"
# file_path = "test_data\\data_demand_random\\15\\R101_2.5.dat"
number_of_trucks = 2
number_of_cities = 0
number_of_drones = 2
truck_speed = 0.5
# drone_speed = 10/6
drone_speed = 1
drone_capacity = 10
drone_limit_time = 90
city_demand = []
release_date = []
unloading_time = 5
service_time = 3
manhattan_move_matrix = []
euclid_flight_matrix = []
city = []
value_tan_of_city = []
DIFFERENTIAL_RATE_RELEASE_TIME = 1
A_ratio = 1
B_ratio = 0.7
C_ratio = 0.1

def read_data(path):
    global data
    global number_of_cities
    global euclid_flight_matrix
    global manhattan_move_matrix
    global city
    global release_date
    global city_demand
    global standard_deviation
    global value_tan_of_city
    global file_name
    global DIFFERENTIAL_RATE_RELEASE_TIME
    global B_ratio
    global C_ratio
    DIFFERENTIAL_RATE_RELEASE_TIME = 1
    A_ratio = 1
    B_ratio = 0.7
    C_ratio = 0.1
    f = open(path)
    data = f.readlines()
    number_of_cities = len(data) - 1
    manhattan_move_matrix = [0] * number_of_cities
    for i in range(number_of_cities):
        manhattan_move_matrix[i] = [0] * number_of_cities
    euclid_flight_matrix = [0] * number_of_cities
    for i in range(number_of_cities):
        euclid_flight_matrix[i] = [0] * number_of_cities
    value_tan_of_city = [0] * number_of_cities
    city = []
    for i in range(1, 1 + number_of_cities):
        city.append([])
        line = data[i].split()
        for j in range(0, 2):
            city[i-1].append(float(line[j]))
    for i in range(number_of_cities):
        for j in range(number_of_cities):
            euclid_flight_matrix[i][j] = euclid_distance(city[i], city[j]) / drone_speed
    euclid_flight_matrix = numpy.array(euclid_flight_matrix)
    for i in range(number_of_cities):
        for j in range(number_of_cities):
            manhattan_move_matrix[i][j] = manhattan_distance(city[i], city[j]) / truck_speed
    manhattan_move_matrix = numpy.array(manhattan_move_matrix)
    for i in range(1, number_of_cities):
        value_tan_of_city[i] = calculate_angle(city[0], city[i])
    release_date = []
    city_demand = [0] * number_of_cities
    for i in range(1, 1 + number_of_cities):
        release_date.append([])
        line = data[i].split()
        release_date[i - 1] = int(line[-1])
        city_demand[i - 1] = int(line[-2])
    standard_deviation = calculate_standard_deviation(release_date)
    # print(standard_deviation)
    return data

def euclid_distance(city1, city2):
    return math.sqrt((city1[0] - city2[0])**2 + (city1[1] - city2[1])**2)

def manhattan_distance(city1, city2):
    return abs(city1[0] - city2[0]) + abs(city1[1] - city2[1])

def calculate_angle(city1, city2):
    if city1[0] != city2[0]:
        delta_x = city2[0] - city1[0]
        delta_y = city2[1] - city1[1]
        angle_rad = math.atan2(delta_y, delta_x)
        angle_deg = math.degrees(angle_rad)
        return angle_deg
    else:
        if city1[1] > city2[1]:
            return -90.0
        if city1[1] < city2[1]:
            return -90.0
        return 0.0 

def read_data2(path):
    global data
    global number_of_cities
    global euclid_flight_matrix
    global manhattan_move_matrix
    global city
    global release_date
    global city_demand
    global standard_deviation
    global value_tan_of_city
    global file_name
    f = open(path)
    data = f.readlines()
    number_of_cities = int(data[0].split()[1])
    manhattan_move_matrix = [0] * number_of_cities
    for i in range(number_of_cities):
        manhattan_move_matrix[i] = [0] * number_of_cities
    euclid_flight_matrix = [0] * number_of_cities
    for i in range(number_of_cities):
        euclid_flight_matrix[i] = [0] * number_of_cities
    value_tan_of_city = [0] * number_of_cities
    city = []
    for i in range(5, 5 + number_of_cities):
        city.append([])
        line = data[i].split()
        for j in range(0, 2):
            city[i-5].append(float(line[j]))
    for i in range(number_of_cities):
        for j in range(number_of_cities):
            euclid_flight_matrix[i][j] = euclid_distance(city[i], city[j]) / drone_speed
    euclid_flight_matrix = numpy.array(euclid_flight_matrix)
    for i in range(number_of_cities):
        for j in range(number_of_cities):
            manhattan_move_matrix[i][j] = manhattan_distance(city[i], city[j]) / truck_speed
    manhattan_move_matrix = numpy.array(manhattan_move_matrix)
    for i in range(1, number_of_cities):
        value_tan_of_city[i] = calculate_angle(city[0], city[i])
    release_date = []
    city_demand = [0] * number_of_cities
    for i in range(5, 5 + number_of_cities):
        release_date.append([])
        line = data[i].split()
        release_date[i - 5] = int(line[-1])
        city_demand[i - 5] = int(line[2])
    standard_deviation = calculate_standard_deviation(release_date)
    # print(standard_deviation)
    return data

def calculate_standard_deviation(arr):
    n = len(arr)
    if n == 0:
        return None

    mean = sum(arr) / n 
    squared_diff = 0
    for i in range(1, len(arr)):
        squared_diff += (arr[i] - mean) ** 2 

    variance = squared_diff / n 
    ratio = 1
    standard_deviation = (variance**0.5) * ratio
    return standard_deviation
 
def read_data_random(path):
    global data
    global number_of_cities
    global euclid_flight_matrix
    global manhattan_move_matrix
    global city
    global release_date
    global city_demand
    global standard_deviation
    global value_tan_of_city
    global file_name
    global DIFFERENTIAL_RATE_RELEASE_TIME
    global B_ratio
    global C_ratio
    
    DIFFERENTIAL_RATE_RELEASE_TIME = 1
    A_ratio = 1
    B_ratio = 0.7
    C_ratio = 0.1
    
    f = open(path)
    data = f.readlines()
    number_of_cities = len(data) - 8
    manhattan_move_matrix = [0] * number_of_cities
    for i in range(number_of_cities):
        manhattan_move_matrix[i] = [0] * number_of_cities
    euclid_flight_matrix = [0] * number_of_cities
    for i in range(number_of_cities):
        euclid_flight_matrix[i] = [0] * number_of_cities
    value_tan_of_city = [0] * number_of_cities
    city = []
    for i in range(8, 8 + number_of_cities):
        city.append([])
        line = data[i].split()
        for j in range(0, 2):
            city[i-8].append(float(line[j]))
    for i in range(number_of_cities):
        for j in range(number_of_cities):
            euclid_flight_matrix[i][j] = euclid_distance(city[i], city[j]) / drone_speed
    euclid_flight_matrix = numpy.array(euclid_flight_matrix)
    for i in range(number_of_cities):
        for j in range(number_of_cities):
            manhattan_move_matrix[i][j] = manhattan_distance(city[i], city[j]) / truck_speed
    manhattan_move_matrix = numpy.array(manhattan_move_matrix)
    for i in range(1, number_of_cities):
        value_tan_of_city[i] = calculate_angle(city[0], city[i])
    release_date = []
    city_demand = [0] * number_of_cities
    for i in range(8, 8 + number_of_cities):
        release_date.append([])
        line = data[i].split()
        release_date[i - 8] = int(line[-1])
        city_demand[i - 8] = int(line[-2])
        # city_demand[i - 8] = 1
    standard_deviation = calculate_standard_deviation(release_date)
    # print(standard_deviation)
    return data
 
def read_data_2024(path, center_type):
    global data
    global number_of_cities
    global euclid_flight_matrix
    global manhattan_move_matrix
    global city
    global release_date
    global city_demand
    global standard_deviation
    global value_tan_of_city
    global file_name
    global DIFFERENTIAL_RATE_RELEASE_TIME
    global B_ratio
    global C_ratio
    DIFFERENTIAL_RATE_RELEASE_TIME = 1
    A_ratio = 1
    B_ratio = 0.7
    C_ratio = 0.1
    f = open(path)
    data = f.readlines()
    number_of_cities = len(data)
    manhattan_move_matrix = [0] * number_of_cities
    for i in range(number_of_cities):
        manhattan_move_matrix[i] = [0] * number_of_cities
    euclid_flight_matrix = [0] * number_of_cities
    for i in range(number_of_cities):
        euclid_flight_matrix[i] = [0] * number_of_cities
    value_tan_of_city = [0] * number_of_cities
    city = []
    city.append([])
    if center_type == "center":
        city[0].append(10)
        city[0].append(10)
    elif center_type == "outside":
        city[0].append(-10)
        city[0].append(10)
    elif center_type == "border":
        city[0].append(0)
        city[0].append(10)
        
    for i in range(1, number_of_cities):
        city.append([])
        line = data[i].split()
        for j in range(1, 3):
            city[i].append(float(line[j]))
    for i in range(number_of_cities):
        for j in range(number_of_cities):
            euclid_flight_matrix[i][j] = euclid_distance(city[i], city[j]) / drone_speed
    euclid_flight_matrix = numpy.array(euclid_flight_matrix)
    for i in range(number_of_cities):
        for j in range(number_of_cities):
            manhattan_move_matrix[i][j] = manhattan_distance(city[i], city[j]) / truck_speed
    manhattan_move_matrix = numpy.array(manhattan_move_matrix)
    for i in range(1, number_of_cities):
        value_tan_of_city[i] = calculate_angle(city[0], city[i])
    release_date = []
    city_demand = [0] * number_of_cities
    release_date.append([])
    release_date[0] = 0
    for i in range(1, number_of_cities):
        release_date.append([])
        line = data[i].split()
        release_date[i] = int(line[0])
        city_demand[i] = 1
    standard_deviation = calculate_standard_deviation(release_date)
    # print(standard_deviation)
    return data
 

# read_data(file_path)

# read_data_random(file_path)

# read_data_2024(file_path, "border")

# read_data_random("test_data\\data_demand_random\\Solomon\\50\\C101_0.5.dat")
