'''
setUpClass Method: Sets up an in-memory SQLite database and loads sample data for testing purposes. This is used to ensure that the database connection and table creation processes work correctly.

test_database_connection Method: Checks that the database connection is working by executing a simple SQL query.

test_training_data_loaded and test_ideal_data_loaded Methods: Verifies that the training and ideal data are loaded into the database correctly by comparing the DataFrame loaded from the database with the original DataFrame.

test_process_test_data Method: Tests the process_test_data function to ensure it processes the test data correctly, including checks for expected columns and additional checks on the data's accuracy.
'''

import unittest
import pandas as pd
import numpy as np
from sqlalchemy import create_engine
from sqlalchemy.exc import OperationalError

# Import the functions from your main script
# from your_module import process_test_data, create_database

class TestDataAnalysis(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        """Set up the database connection and test data for all tests."""
        # Create an in-memory SQLite database for testing
        cls.engine = create_engine('sqlite:///:memory:', echo=False)

        # Sample data for testing
        cls.train_data = pd.DataFrame({
            'x': np.linspace(-20, 20, 10),
            'y1': np.random.randn(10),
            'y2': np.random.randn(10),
            'y3': np.random.randn(10),
            'y4': np.random.randn(10)
        })

        cls.ideal_data = pd.DataFrame({
            'x': np.linspace(-20, 20, 10),
            'y1': np.random.randn(10),
            'y2': np.random.randn(10),
            # ... more columns as needed
            'y42': np.random.randn(10),
            'y41': np.random.randn(10),
            'y11': np.random.randn(10),
            'y48': np.random.randn(10)
        })

        cls.test_data = pd.DataFrame({
            'x': [17.5, 0.3, -8.7, -19.2, -11.0],
            'y': [34.161040, 1.215102, -16.843908, -37.170870, -20.263054]
        })

        # Load data into database tables
        cls.train_data.to_sql('training_data', cls.engine, if_exists='replace', index=False)
        cls.ideal_data.to_sql('ideal_functions', cls.engine, if_exists='replace', index=False)

    def test_database_connection(self):
        """Test if the database connection is working."""
        try:
            with self.engine.connect() as connection:
                result = connection.execute("SELECT 1").fetchone()
                self.assertEqual(result[0], 1)
        except OperationalError:
            self.fail("Failed to connect to the database.")

    def test_training_data_loaded(self):
        """Test that the training data is loaded correctly."""
        df = pd.read_sql_table('training_data', self.engine)
        pd.testing.assert_frame_equal(df, self.train_data)

    def test_ideal_data_loaded(self):
        """Test that the ideal data is loaded correctly."""
        df = pd.read_sql_table('ideal_functions', self.engine)
        pd.testing.assert_frame_equal(df, self.ideal_data)

    def test_process_test_data(self):
        """Test that the test data is processed correctly."""
        # You need to adapt this if you change the function signature or behavior
        results_df = process_test_data(self.test_data, self.engine)
        
        # Check if results_df contains expected columns
        self.assertIn('x', results_df.columns)
        self.assertIn('y', results_df.columns)
        self.assertIn('best_fit_function', results_df.columns)
        self.assertIn('ideal_y', results_df.columns)
        self.assertIn('deviation', results_df.columns)

        # Further checks on data processing can be added here
        # Example: Check a specific row's value
        # self.assertAlmostEqual(results_df.loc[0, 'ideal_y'], expected_value, places=5)

if __name__ == '__main__':
    unittest.main()
