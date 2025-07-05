import pandas as pd

# Define the data
# data = [
#     [7.77, 7.32],
#     [6.29, 7.18],
#     [18.86, 51.37],
#     [5.55, 5.65],
#     [8.69, 9.1],
#     [45.64, 34.18],
#     [8.63, 9.24],
#     [41.93, 40.01],
#     [7.5, 7.82, 9.84],
#     [7.04, 7.01, 7.81],
#     [25.57, 8.69, 33.29],
#     [5.7, 5.84, 5.73],
#     [8.32, 8.36, 8.82],
#     [30.22, 18.53, 32.37],
#     [8.17, 9.01, 9.0],
#     [23.38, 25.25, 33.56]
# ]


# Jain's Fairness Index calculation function
def jains_fairness_index(data_row):
    n = len(data_row)
    sum_data = sum(data_row)
    sum_data_squared = sum_data ** 2
    sum_of_squares = sum(x ** 2 for x in data_row)
    return sum_data_squared / (n * sum_of_squares)

# Apply the function to each row of data
fairness_indices = [jains_fairness_index(row) for row in data]

# Create a DataFrame for better readability
df = pd.DataFrame({
    "Data": data,
    "Jain's Fairness Index": fairness_indices
})

# Display the result
print(df)
