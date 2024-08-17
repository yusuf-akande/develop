'''
1. Create and Set Up a SQLite Database: Use SQLAlchemy to set up a SQLite database, creating tables for training data, ideal functions, and test data.
2. Load Data into the Database: Load the training data and ideal functions into the respective tables. Load the test data line-by-line.
3. Select Ideal Functions: Use the least squares method to choose the four best ideal functions that fit the training data.
4. Map Test Data: For each test data point, determine if it can be assigned to one of the four chosen ideal functions and compute deviations.
5. Visualize the Results: Plot the training data, selected ideal functions, and test data with deviations.

'''

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sqlalchemy import create_engine
from sqlalchemy.types import Float, Integer

# Create a SQLite database using SQLAlchemy
# https://docs.sqlalchemy.org/en/20/tutorial/engine.html

engine = create_engine('sqlite:///data_analysis.db', echo=False)

# Load training data CSV files into a single DataFrame
train_files = ['../data/train1.csv', '../data/train2.csv', '../data/train2.csv', '../data/train2.csv']
train_data = pd.concat([pd.read_csv(file) for file in train_files], axis=1)
train_data.columns = ['x', 'y1', 'y2', 'y3', 'y4']

# Save the training data to a SQLite table
train_data.to_sql('training_data', engine, if_exists='replace', index=False, dtype={'x': Float, 'y1': Float, 'y2': Float, 'y3': Float, 'y4': Float})

# Load the ideal functions into another table
# https://pandas.pydata.org/docs/user_guide/io.html

ideal_df = pd.read_csv('/path/to/ideal.csv')
ideal_df.to_sql('ideal_functions', engine, if_exists='replace', index=False)


'''
Use the training data to identify the four ideal functions from the ideal dataset 
by minimizing the least squares criterion.
'''

# Extract the x-values and y-values from the training data
x_train = train_data['x']
y_train_values = train_data.iloc[:, 1:]

# Extract the y-values from the ideal data (excluding the x column)
y_ideal_values = ideal_df.iloc[:, 1:]

# Compute the least squares error for each training function against all ideal functions
least_squares_errors = np.zeros((y_train_values.shape[1], y_ideal_values.shape[1]))

for i in range(y_train_values.shape[1]):
    for j in range(y_ideal_values.shape[1]):
        least_squares_errors[i, j] = np.sum((y_train_values.iloc[:, i] - y_ideal_values.iloc[:, j]) ** 2)

# Find the indices of the four ideal functions with the smallest errors for each training function
best_fit_indices = np.argmin(least_squares_errors, axis=1)

# Get the names of the selected ideal functions
selected_ideal_functions = ideal_df.columns[1:][best_fit_indices]

# View selected ideal functions
selected_ideal_functions

# The four ideal functions selected based on the least squares criterion are:

# For y1: y42
# For y2: y41
# For y3: y11
# For y4: y48


# Function to process and match test data
def process_test_data(test_file):
    test_results = []
    
    # Load the test data line-by-line
    with open(test_file, 'r') as f:
        test_df = pd.read_csv(f)
        
    for _, test_point in test_df.iterrows():
        x_test = test_point['x']
        y_test = test_point['y']

        # Query the ideal functions for the corresponding x value
        ideal_y_values = pd.read_sql_query(f"SELECT y42, y41, y11, y48 FROM ideal_functions WHERE x = {x_test}", engine)

        if not ideal_y_values.empty:
            deviations = np.abs(ideal_y_values.iloc[0] - y_test)
            min_deviation = deviations.min()
            best_fit_function = deviations.idxmin()
            
            # Store the result
            test_results.append({
                'x': x_test,
                'y': y_test,
                'best_fit_function': best_fit_function,
                'ideal_y': ideal_y_values[best_fit_function].values[0],
                'deviation': min_deviation
            })
            
    return pd.DataFrame(test_results)

# Process test data and store results
test_results_df = process_test_data('/path/to/test.csv')
test_results_df.to_sql('test_results', engine, if_exists='replace', index=False, dtype={'x': Float, 'y': Float, 'ideal_y': Float, 'deviation': Float, 'best_fit_function': Integer})

# Plotting
def plot_results():
    plt.figure(figsize=(14, 8))

    # Plot training data
    for col in ['y1', 'y2', 'y3', 'y4']:
        plt.plot(train_data['x'], train_data[col], label=f'Training {col}', linestyle='--')

    # Plot selected ideal functions
    for col in ['y42', 'y41', 'y11', 'y48']:
        plt.plot(ideal_df['x'], ideal_df[col], label=f'Ideal {col}', linewidth=2)

    # Plot test data with annotations
    plt.scatter(test_results_df['x'], test_results_df['y'], color='red', label='Test Data', zorder=5)
    for _, row in test_results_df.iterrows():
        plt.annotate(row['best_fit_function'], (row['x'], row['y']), textcoords="offset points", xytext=(5, -10), ha='center')

    plt.xlabel('x')
    plt.ylabel('y')
    plt.title('Data Analysis: Training, Ideal, and Test Data with Deviations')
    plt.legend()
    plt.grid(True)
    plt.show()

plot_results()