# Importing important libraries to run the program (data, calulations, and graphing)
import pandas as pd 
import numpy as np 
import matplotlib.pyplot as plt

# Loading the CPI data from CSV file and skipping the first 8 rows of header information
def load_cpi_data(filename):
    df = pd.read_csv(filename, skiprows=8)
    df.columns = ['date', 'CPI', 'extra1', 'extra2']
    df = df[['date', 'CPI']].dropna()

    # Split the date string (format M/D/YY) into parts so python can read it as month, day, and year instead of text string 
    df['month'] = df['date'].str.split('/').str[0].astype(int)
    df['year']  = df['date'].str.split('/').str[2].astype(int)

    # The CSV uses 2 digits for the year and python doesn't know if it's 1900s or the 2000s, so this line helps python know which century to use (greater than 14 is 1900s, otherwise 2000s)
    df['year'] = df['year'].apply(lambda x: x + 1900 if x >= 14 else x + 2000)
    
    # Combining year and month columns into proper date format
    df['date'] = pd.to_datetime(df[['year', 'month']].assign(day=1))

    # Convert CPI to numbers and drop any rows with missing values (helped my program from crashing)
    df['CPI'] = pd.to_numeric(df['CPI'], errors='coerce')
    df = df.dropna()

    # Sort data chronologically and reset row numbers 
    df = df.sort_values('date').reset_index(drop=True)

    # Filter data to only show data from 1950 to 2026. This stopped the graph from being abnormally skewed and made the graph more readable
    df = df[(df['date'].dt.year >= 1950) & (df['date'].dt.year <= 2026)]

    return df

# Function to calculate annual percentnage change in CPI
def calculate_annual_percentage_change(df):
    df['annual_change'] = df['CPI'].pct_change(periods=12) * 100
    return df   

# Function to plot CPI time series and annual percentage change on the dual-axis graph
def plot_cpi(df):
    fig, ax1 = plt.subplots(figsize=(12, 6))

    # Plotting CPI on the left axis 
    ax1.plot(df['date'], df['CPI'], color='pink', label = 'CPI')
    ax1.set_xlabel('Year')
    ax1.set_ylabel('CPI level', color='pink')

    # add dotted line at base level (CPI = 100)
    ax1.axhline (y=100, color='navy', linestyle = '--', label = 'Base level (100)')

    # Create second y-axis on right side for the annual percentage change
    ax2 = ax1.twinx()
    ax2.plot(df['date'], df['annual_change'], color='orange',label='Annual Percentage Change')
    ax2.set_ylabel('Annual Percentage Change', color='orange')

    # Add our title and legend
    plt.title('Canadian CPI Time Series')
    fig.legend (loc='upper left')
    plt.tight_layout()

    # Save the graph as PNG file and display it
    plt.savefig('Canadian_CPI_Time_Series.png')
    plt.show()


# To run the bank of canada inflation calculator with inputs of months and years
def inflation_calculator(df):

# Get dollar amount from user and adding measures to prevent crashing caused by letters and negative numnbers
    while True:
        try:
            amount = float (input("Enter dollar amount you want to calculate inflation for: "))
            if amount <= 0:
                print ("enter number greater than 0")
                continue
            break
        except ValueError:
            print("Please enter a valid number.")
            continue
    
 # Get starting month and year and adding measures to prevent inputs outside of the dataset.
    while True:
        try:
            start_month = int(input("Enter starting month (1-12): "))
            start_year = int(input("Enter starting year (1950-2015): "))
            if not (1 <= start_month <= 12):
                print("Month must be between 1 and 12.")
                continue
            if not (1950 <= start_year <= 2015):
                print("Year must be between 1950 and 2015.")
                continue
            start_data = df[(df['date'].dt.month == start_month) & (df['date'].dt.year == start_year)]
            if start_data.empty:
                print("No data for that date. Try another.")
                continue
            cpi_start = start_data['CPI'].values[0]
            break
        except ValueError:
            print("Enter whole numbers only.")
            continue

# Same process and error measurement as starting month and year but flipped for ending month and year
    while True:
        try:
            end_month = int(input("Enter ending month (1-12): "))
            end_year = int(input("Enter ending year (1950-2015): "))
            if not (1 <= end_month <= 12):
                print("Month must be between 1 and 12.")
                continue
            if not (1950 <= end_year <= 2015):
                print("Year must be between 1950 and 2015.")
                continue
            end_data = df[(df['date'].dt.month == end_month) & (df['date'].dt.year == end_year)]
            if end_data.empty:
                print("No data for that date. Try another.")
                continue
            cpi_end = end_data['CPI'].values[0]
            break
        except ValueError:
            print("Enter whole numbers only.")
            continue

# Calculate results using NumPy to match BoC inflation calculator
    # this is for price in second period
    adjusted_amount = np.round(amount * (cpi_end / cpi_start), 2)
    # total percent change in prices 
    percent_change = np.round(((cpi_end - cpi_start) / cpi_start) * 100, 2)
    # years between the two periods 
    num_years = np.round((end_year + end_month / 12) - (start_year + start_month / 12), 2)
    # compound annual rate of change 
    if num_years != 0:
        annual_rate = np.round(((cpi_end / cpi_start) ** (1 / num_years) - 1) * 100, 2)
    else:
        annual_rate = 0.0

    # Display results to look like the BoC calculator
    print("Results")
    print(f"  ${amount:,.2f} CAD in {start_month:02d}/{start_year}")
    print(f"  would cost ${adjusted_amount:,.2f} CAD in {end_month:02d}/{end_year}.")
    print(f"\n  Percent change       : {percent_change:.2f}%")
    print(f"  Number of years      : {num_years:.2f}")
    print(f"  Annual rate of change: {annual_rate:.2f}%")
    print(f"\n  CPI {start_month:02d}/{start_year}          : {cpi_start:.1f}")
    print(f"  CPI {end_month:02d}/{end_year}          : {cpi_end:.1f}")
    print(f"  (Base year: 2002 = 100.0)")

# Main block to run my program :)
df = load_cpi_data('CPI_Python_data.csv')
df = calculate_annual_percentage_change(df)
plot_cpi(df)    
inflation_calculator(df)
