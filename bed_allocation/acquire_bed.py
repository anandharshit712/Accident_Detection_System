from hospital_data import *

def get_bed_value_by_id(hospital_id):
    for hid, details in hospital_dict.items():
        if hid == hospital_id :
            return details['no_of_available_beds']
    return None # Return None if the Id is not found


def acquire_beds(hospital_queue, avg_bed):
    bed_allocation = {}
    beds_required = avg_bed
    while beds_required > 0 and hospital_queue :
        element = hospital_queue.pop(0)
        distance, h_id = element[0],element[1]
        bed_value = get_bed_value_by_id(h_id)
        if bed_value <= beds_required:
            bed_allocation['h_id'] = h_id
            bed_allocation['bed_value'] = beds_required
            beds_required -= bed_value
        else:
            bed_allocation['h_id'] = h_id
            bed_allocation['bed_value'] = beds_required
            beds_required = 0
        #print(f"Acquired {bed_allocation[h_id]} beds from hospital {h_id}")
    return bed_allocation
