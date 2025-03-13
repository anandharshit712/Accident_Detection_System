from hospital_pq import *
from fetch_all_user import *
from bed_approximation import appox
from acquire_bed import *
from hospital_data import *
from post_json import *

Id_map_accident = {}
no_of_beds, latitudes, longitudes, mob = fetch_no_of_beds()
avg_beds = [appox(beds) for beds in no_of_beds]
hospital_queue_mat = [return_priority_queue(lat,long) for lat,long in zip(latitudes,longitudes)]

for i in range(len(avg_beds)):
    Id_map_accident["accident"+f"{i}"] =  acquire_beds(hospital_queue_mat[i],avg_beds[i])

print(Id_map_accident)
to_alert = []
for accident,doc in Id_map_accident.items():
    temp_dict = {"hospital_id": doc['h_id'],"mobileNumber": mob.pop(0),"latitude": latitudes.pop(0),"longitude": longitudes.pop(0),"noOfBeds": doc['bed_value']}
    to_alert.append(temp_dict)

print(to_alert)
#post_to_mongodb(to_alert)