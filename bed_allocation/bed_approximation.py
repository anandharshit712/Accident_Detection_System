import numpy as np

#data = [10, 20, 30, 40, 50, 1000]
def appox(data):
    # Identify outliers using the IQR method
    Q1 = np.percentile(data, 25)
    Q3 = np.percentile(data, 75)
    IQR = Q3 - Q1
    lower_bound = Q1 - 1.5 * IQR
    upper_bound = Q3 + 1.5 * IQR

    # Remove outliers
    filtered_data = [x for x in data if lower_bound <= x <= upper_bound]

    # Calculate the average
    average = np.mean(filtered_data)
    return round(average)

