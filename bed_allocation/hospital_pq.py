from hospital_data import hospital_dict
from queue import PriorityQueue
import math

def return_priority_queue(lat, long):
    pq = PriorityQueue()

    def euclidean_distance(coord1, coord2):
        lat1, lon1 = coord1
        lat2, lon2 = coord2
        return math.sqrt((lat1 - lat2) ** 2 + (lon1 - lon2) ** 2)

    def find_k_nearest_neighbors(input_coordinate, k=10):
        distances = []
        for hid, details in hospital_dict.items():
            lati = details['latitude']
            longi = details['longitude']
            distance = euclidean_distance(input_coordinate, (lati,longi))
            distances.append((hid, distance))

        distances.sort(key=lambda x: x[1])
        nearest_neighbors = distances[:k]
        return nearest_neighbors

    input_coordinate = (lat, long)
    nearest_hospitals = find_k_nearest_neighbors(input_coordinate)

    for hid, distance in nearest_hospitals:
        pq.put((distance, hid))

    def convert_pq_to_list(pq):
        pq_list = []
        while not pq.empty():
            pq_list.append(pq.get())
        return pq_list

    return convert_pq_to_list(pq)





