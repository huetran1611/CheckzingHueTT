import Data
import Function
import Neighborhood
import time
import random
import csv
import Neighborhood11
import Neighborhood10
import Neighborhood_drone

global LOOP
global tabu_tenure
# global best_sol
# global best_fitness
global Tabu_Structure
global current_neighborhood
global LOOP_IMPROVED
global SET_LAST_10
global BEST
global start_time
global Data1
epsilon = (-1)*0.00001


sol = [[[[0, []], [9, [9]]], [[0, []], [10, [10]], [5, [5]], [0, []], [6, [6, 3]], [3, []], [8, [8]], [7, [7, 2]], [2, []], [4, [4, 1]], [1, []]]], [[[9, [9]]], [[10, [10]]], [[5, [5]]], [[6, [6, 3]]], [[8, [8]]], [[7, [7, 2]]], [[4, [4, 1]]]]]


sol = [sol, Function.fitness(sol)]
min_to_improve = sol[1][0]
besst = sol
# list_neighborhood = [Neighborhood_drone.Neighborghood_change_drone_route_max_pro_plus_for_specific_truck, Neighborhood_drone.Neighborhood_group_trip]
# list_neighborhood = [Neighborhood_drone.Neighborghood_change_drone_route_max_pro_plus_for_specific_truck, Neighborhood_drone.Neighborhood_change_index_trip, Neighborhood_drone.Neighborhood_group_trip]       
list_neighborhood = [Neighborhood_drone.Neighborghood_change_drone_route_max_pro_plus, Neighborhood_drone.Neighborhood_change_index_trip]       
j = 0
while j < 2:
    j += 1
    # print("i: ",i," j: ", j)
    # print(sol[0])
    for k in range(len(list_neighborhood)):
        # print(sol[0])
        print(k)
        print(sol)
        drone_neighborhood = list_neighborhood[k](sol[0])
        min_in_loop = 1000000
        next_index = 0
        if len(drone_neighborhood) == 0:
            continue
        for l in range(len(drone_neighborhood)):
            cfnode = drone_neighborhood[l][1][0]
            if cfnode - min_to_improve < epsilon:
                besst = drone_neighborhood[l]
                next_index = l
                min_in_loop = cfnode
                min_to_improve = cfnode
                j = 0
            elif cfnode - min_in_loop < epsilon:
                next_index = l
                min_in_loop = cfnode
        sol = drone_neighborhood[next_index]
