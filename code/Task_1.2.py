# Importing required libraries
import pandas as pd
import yfinance as yf
from bokeh.plotting import figure, show
from bokeh.io import output_file
from bokeh.models import ColumnDataSource
from sqlalchemy import create_engine, Column, Integer, String, Float, Date
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import unittest
from datetime import datetime, timedelta


# Define custom exceptions
class StockDataError(Exception):
    """Exception raised for errors in stock data retrieval."""
    pass

class DatabaseError(Exception):
    """Exception raised for errors in database operations."""
    pass

# Define base class for financial instruments

# states start and end date for yfinance
start_date="2023-01-01"
end_date="2023-12-31"

class FinancialInstrument:
    """Base class for financial instruments."""
    
    def __init__(self, symbol):
        """
        Initialize the financial instrument.
        
        :param symbol: The ticker symbol of the instrument
        """
        self.symbol = symbol
        self.data = None
    
    def fetch_data(self, start_date, end_date):
        """
        Fetch data for the financial instrument.
        
        :param start_date: Start date for data retrieval
        :param end_date: End date for data retrieval
        """
        raise NotImplementedError("Subclass must implement abstract method")

# Define Stock class that inherits from FinancialInstrument
class Stock(FinancialInstrument):
    """Class representing a stock, inheriting from FinancialInstrument."""
    
    def fetch_data(self, start_date, end_date):
        """
        Fetch stock data using yfinance.
        
        :param start_date: Start date for data retrieval
        :param end_date: End date for data retrieval
        :raises StockDataError: If there's an error fetching stock data
        """
        try:
            self.data = yf.download(self.symbol, start=start_date, end=end_date)
            if self.data.empty:
                raise StockDataError(f"No data available for {self.symbol}")
        except Exception as e:
            raise StockDataError(f"Error fetching data for {self.symbol}: {str(e)}")

# Set up SQLAlchemy
Base = declarative_base()

class StockPrice(Base):
    """SQLAlchemy model for stock prices."""
    
    __tablename__ = 'stock_prices'
    
    id = Column(Integer, primary_key=True)
    symbol = Column(String(10))
    date = Column(Date)
    open = Column(Float)
    high = Column(Float)
    low = Column(Float)
    close = Column(Float)
    volume = Column(Integer)

# Database manager class
db_url = 'sqlite:///stockmarket.db'
class DatabaseManager:
    """Class to manage database operations."""
    
    def __init__(self, db_url):
        """
        Initialize the database manager.
        
        :param db_url: URL for the database connection
        """
        
        self.engine = create_engine(db_url, echo=False)
        Base.metadata.create_all(self.engine)
        self.Session = sessionmaker(bind=self.engine)
    
    def save_stock_data(self, stock):
        """
        Save stock data to the database.
        
        :param stock: Stock object containing data to be saved
        :raises DatabaseError: If there's an error saving data to the database
        """
        session = self.Session()
        try:
            for date, row in stock.data.iterrows():
                price = StockPrice(
                    symbol=stock.symbol,
                    date=date.date(),
                    open=row['Open'],
                    high=row['High'],
                    low=row['Low'],
                    close=row['Close'],
                    volume=row['Volume']
                )
                session.add(price)
            session.commit()
        except Exception as e:
            session.rollback()
            raise DatabaseError(f"Error saving data to database: {str(e)}")
        finally:
            session.close()

# Visualization class
class StockVisualizer:
    """Class to create visualizations for stock data."""
    
    @staticmethod
    def create_candlestick_chart(stock, output_filename="stock"):
        """
        Create a candlestick chart using Bokeh.
        
        :param stock: Stock object containing data to be visualized
        :param output_filename: Filename for the output HTML file
        """
        df = stock.data.reset_index()
        source = ColumnDataSource(data=dict(
            date=df['Date'],
            open=df['Open'],
            high=df['High'],
            low=df['Low'],
            close=df['Close']
        ))
        
        p = figure(x_axis_type="datetime", title=f"{stock.symbol} Candlestick Chart", width=1000, height=400)
        p.segment('date', 'high', 'date', 'low', color="black", source=source)
        p.vbar('date', 0.5, 'open', 'close', fill_color="green", line_color="black", source=source)
        
        output_file(output_filename)
        show(p)

# Main application class
class StockAnalysisApp:
    """Main application class for stock analysis."""
    
    def __init__(self, db_url):
        """
        Initialize the stock analysis application.
        
        :param db_url: URL for the database connection
        """
        self.db_manager = DatabaseManager(db_url)
    
    def run_analysis(self, symbol, start_date, end_date):
        """
        Run stock analysis for a given symbol and date range.
        
        :param symbol: Stock symbol to analyze
        :param start_date: Start date for analysis
        :param end_date: End date for analysis
        """
        try:
            stock = Stock(symbol)
            stock.fetch_data(start_date, end_date)
            self.db_manager.save_stock_data(stock)
            
            visualizer = StockVisualizer()
            visualizer.create_candlestick_chart(stock, f"{symbol}_candlestick.html")
            
            print(f"Analysis completed for {symbol}. Candlestick chart saved as {symbol}_candlestick.html")
        except (StockDataError, DatabaseError) as e:
            print(f"Error during analysis: {str(e)}")

# Unit tests
class TestStockAnalysis(unittest.TestCase):
    """Unit tests for the stock analysis system."""
    
    def setUp(self):
        """Set up test environment."""
        self.stock = Stock("AAPL")
    
    def test_stock_initialization(self):
        """Test stock initialization."""
        self.assertEqual(self.stock.symbol, "AAPL")
        self.assertIsNone(self.stock.data)
    
    def test_stock_data_fetching(self):
        """Test stock data fetching."""
        end_date = datetime.now().date()
        start_date = end_date - timedelta(days=30)
        self.stock.fetch_data(start_date, end_date)
        self.assertIsNotNone(self.stock.data)
        self.assertFalse(self.stock.data.empty)

# Run unit tests
if __name__ == '__main__':
    unittest.main(argv=[''], exit=False)

print("Stock analysis system and unit tests defined successfully.")
# Example usage
app = StockAnalysisApp(db_url)
result = app.run_analysis('AAPL', start_date, end_date)
print(result)
print(app.db_manager.save_stock_data('AAPL'))
