import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
# !pip install mplfinance
import mplfinance as mpf
from datetime import datetime
import os
from PIL import Image

# Load the configuration
acct_id = '8908'

start_year = 2024
end_year = 2024

start_month = 4
end_month = 4

start_day = 15
end_day = 19

period_string = "Weekly"

start_date = datetime(start_year, start_month, start_day)
end_date = datetime(end_year, end_month, end_day)

pd_date_extraction = pd.date_range(start = start_date, end = end_date, freq = "D")
date_extraction = pd_date_extraction.strftime("%Y%m%d")
# This is an estimate based on how much we can expect balance to sharply change based on user external input to withdraw or change balance
diff_percentage = 0.25

# Change output file name to one that you want
output_filename = str(acct_id)+"_"+str(period_string)+"_Performance("+date_extraction[0]+"-"+date_extraction[-1]+").csv"
print(output_filename)

# Put the exact name that you used to make a folder inside the google colab
internal_foldername = str(acct_id)+"_data"
print(internal_foldername)

# this data is for candlestick chart pattern
time_frequency = "2H" # hourly specify
output_title = str(acct_id)+"_"+str(period_string)+"_Performance("+date_extraction[0]+"-"+date_extraction[-1]+")"
output_filename_candlestick = str(acct_id)+"_"+str(period_string)+"_Performance("+date_extraction[0]+"-"+date_extraction[-1]+")_Candlestick_Pattern.csv"
print(output_filename_candlestick)

# --------------------------------------------

# Part 1: Combining Multiple CSV Together

## Extract CSV According to our Inputs
directory = internal_foldername

csv_files = []
# List the CSV files in the directory
for date in date_extraction:
  csv = [f for f in os.listdir(directory) if f.endswith(date+'.csv')]
  if (len(csv)>0): csv_files.append(csv) # only append if a file is found

# convert list of lists in 1-D array
csv_files = np.reshape(csv_files, -1)
print(csv_files)

df_list = []

# Loop through the CSV files and load them into DataFrames
count = 0
for file in csv_files:
    # count += 1
    # print(count)
    # Load the CSV file into a DataFrame
    df = pd.read_csv(os.path.join(directory, file), usecols = range(12))
    # Append the DataFrame to the list
    df_list.append(df)
    # try:
    #   df = pd.read_csv(os.path.join(directory, file),usecols=range(12))
    #   df_list.append(df)
    # except pd.errors.ParserError as e:
    #   print(f"Error reading file {file}: {e}")

## Data Cleaning
columns_to_numbers = ["Balance", "Equity", "Delta", "% Difference",
                      "Highest Balance", "Lowest Balance",
                      "Highest Equity", "Lowest Equity",
                      "Used Margin", "Free Margin"]


df_list_updated = []

# go into each df csv and add the columns and calculations
count =0
for df in df_list:
  count+=1
  print(count)
  for col in columns_to_numbers:
    df[col] = pd.to_numeric(df[col], errors="coerce")


  df["Starting Day Balance"] = df["Balance"][0]
  df["Starting Day Equity"] = df["Equity"][0]

  # Before calculations, if there is a big change in balance (withdrawn or balance changed by user) then change starting day balance and equity accordingly
  prev_row = [0.0 for i in range(len(df)-1)]
  current_row = [0.0 for i in range(len(df)-1)]
  diff_row = [0.0 for i in range(len(df))] # current row - prev row
  diff_percentage_row = [0.0 for i in range(len(df))]
  big_change_row = [False for i in range(len(df))]

  prev_row = df["Balance"][:-1]
  current_row = df["Balance"][1:]

  prev_row.reset_index(drop = True)
  current_row.reset_index(drop = True)

  prev_row = np.array(prev_row)
  current_row = np.array(current_row)
  diff_row = np.array(diff_row)
  diff_row[1:] = np.abs(current_row - prev_row)
  diff_percentage_row[1:] = diff_row[1:]/prev_row

  diff_percentage_row = np.array(diff_percentage_row)
  big_change_row = np.array(big_change_row)
  big_change_row = diff_percentage_row > diff_percentage

  indices_change = np.argwhere(big_change_row)
  indices_change = np.array(indices_change).reshape(-1,)
  indices_change = np.sort(indices_change)
  for index in indices_change:
    df["Starting Day Balance"][index:] = df["Balance"][index]
    df["Starting Day Equity"][index:] = df["Equity"][index]

  # Adding new columns to it
  df["% Difference from Balance"] = (df["Equity"] - df["Starting Day Balance"])/df["Starting Day Balance"]
  df["% Difference from Equity"] = (df["Equity"] - df["Starting Day Equity"])/df["Starting Day Equity"]

  df_list_updated.append(df)


df = pd.concat(df_list_updated, ignore_index=True)


# Delete NA rows and columns headers if mixed within the data
print("Number of data:", len(df))
indices_to_drop = df[df["Time"] == "Time"].index
df.drop(indices_to_drop, inplace=True)
df.dropna(inplace=True)
print()
print("Number of updated rows:", len(df))

df["Date"] = pd.to_datetime(df["Date"], format="%Y.%m.%d")
# try:
#     df["Date"] = pd.to_datetime(df["Date"], format="%Y.%m.%d")
# except ValueError as e:
#     print(f"Error converting date to datetime: {e}")
#     problematic_values = df.loc[pd.to_datetime(df["Date"], errors='coerce').isna(), "Date"]
#     print(f"Problematic values: {problematic_values}")

df["Time"] = pd.to_datetime(df["Time"], format="%H:%M:%S").dt.time

# for col in columns_to_numbers:
#     df[col] = pd.to_numeric(df[col], errors="coerce")
df["% Difference from Balance"] = pd.to_numeric(df["% Difference from Balance"], errors = "coerce")
df["% Difference from Equity"] = pd.to_numeric(df["% Difference from Equity"], errors = "coerce")

df = df.sort_values(by=["Date", "Time"])
df = df.reset_index(drop=True)
df

## Output Combined CSV Files
df.to_csv(output_filename, index = False)

# --------------------------------------------
# Part 2: CandleStick Chart Output

## Combined CSV file partioned in time interval
# end_day + 1 needs to be done to get data for end_day in candlestick chart
time_interval = pd.date_range(start=start_date, end=datetime(end_year, end_month, end_day+1), freq=time_frequency)

time_partition_arraylist = []

df["Time"] = pd.to_datetime(df["Time"], format="%H:%M:%S")
# df.info()
# df["Time"][0]
df["DateTime"] = df["Date"] + (df["Time"] - datetime(1900, 1, 1, 0, 0, 0)) # normalize and combine date and time
# df["DateTime"]
for i in range(len(time_interval)-1):
  time_partition_arraylist.append(df[(df["DateTime"]>=time_interval[i]) & (df["DateTime"]<time_interval[i+1])])

## Making a new CSV table with candlestick chart style data
df_time_partition = pd.DataFrame(index=range(len(time_partition_arraylist)))

# Balance
# df_time_partition["DateTime"] = df["DateTime"]
df_time_partition["DateTime"] = time_interval[:-1]
df_time_partition["Balance Open"] = 0.0
df_time_partition["Balance Close"] = 0.0
df_time_partition["Balance High"] = 0.0
df_time_partition["Balance Low"] = 0.0

# Equity
df_time_partition["Equity Open"] = 0.0
df_time_partition["Equity Close"] = 0.0
df_time_partition["Equity High"] = 0.0
df_time_partition["Equity Low"] = 0.0

# Used Margin
df_time_partition["Used Margin Open"] = 0.0
df_time_partition["Used Margin Close"] = 0.0
df_time_partition["Used Margin High"] = 0.0
df_time_partition["Used Margin Low"] = 0.0

# Free Margin
df_time_partition["Free Margin Open"] = 0.0
df_time_partition["Free Margin Close"] = 0.0
df_time_partition["Free Margin High"] = 0.0
df_time_partition["Free Margin Low"] = 0.0

# % Difference from Balance
df_time_partition["% Difference from Balance Open"] = 0.0
df_time_partition["% Difference from Balance Close"] = 0.0
df_time_partition["% Difference from Balance High"] = 0.0
df_time_partition["% Difference from Balance Low"] = 0.0

# % Difference from Equity
df_time_partition["% Difference from Equity Open"] = 0.0
df_time_partition["% Difference from Equity Close"] = 0.0
df_time_partition["% Difference from Equity High"] = 0.0
df_time_partition["% Difference from Equity Low"] = 0.0


for i in range(len(time_partition_arraylist)):
  # df_time_partition["Time"][i] = time_interval[i+1]
  if (len(time_partition_arraylist[i])==0):
    if (i==0):
      # balance
      df_time_partition["Balance Open"][i] = df["Balance"][i]
      df_time_partition["Balance Close"][i] = df["Balance"][i]
      df_time_partition["Balance High"][i] = df["Balance"][i]
      df_time_partition["Balance Low"][i] = df["Balance"][i]

      # equity
      df_time_partition["Equity Open"][i] = df["Equity"][i]
      df_time_partition["Equity Close"][i] = df["Equity"][i]
      df_time_partition["Equity High"][i] = df["Equity"][i]
      df_time_partition["Equity Low"][i] = df["Equity"][i]

      # used margin
      df_time_partition["Used Margin Open"][i] = df["Used Margin"][i]
      df_time_partition["Used Margin Close"][i] = df["Used Margin"][i]
      df_time_partition["Used Margin High"][i] = df["Used Margin"][i]
      df_time_partition["Used Margin Low"][i] = df["Used Margin"][i]

      # free margin
      df_time_partition["Free Margin Open"][i] = df["Free Margin"][i]
      df_time_partition["Free Margin Close"][i] = df["Free Margin"][i]
      df_time_partition["Free Margin High"][i] = df["Free Margin"][i]
      df_time_partition["Free Margin Low"][i] = df["Free Margin"][i]

      # % Difference from Balance
      df_time_partition["% Difference from Balance Open"][i] = df["% Difference from Balance"][i]
      df_time_partition["% Difference from Balance Close"][i] = df["% Difference from Balance"][i]
      df_time_partition["% Difference from Balance High"][i] = df["% Difference from Balance"][i]
      df_time_partition["% Difference from Balance Low"][i] = df["% Difference from Balance"][i]

      # % Difference from Equity
      df_time_partition["% Difference from Equity Open"][i] = df["% Difference from Equity"][i]
      df_time_partition["% Difference from Equity Close"][i] = df["% Difference from Equity"][i]
      df_time_partition["% Difference from Equity High"][i] = df["% Difference from Equity"][i]
      df_time_partition["% Difference from Equity Low"][i] = df["% Difference from Equity"][i]

    else:
      # balance
      df_time_partition["Balance Open"][i] = df_time_partition["Balance Close"][i-1]
      df_time_partition["Balance Close"][i] = df_time_partition["Balance Close"][i-1]
      df_time_partition["Balance High"][i] = df_time_partition["Balance Close"][i-1]
      df_time_partition["Balance Low"][i] = df_time_partition["Balance Close"][i-1]

      # equity
      df_time_partition["Equity Open"][i] = df_time_partition["Equity Close"][i-1]
      df_time_partition["Equity Close"][i] = df_time_partition["Equity Close"][i-1]
      df_time_partition["Equity High"][i] = df_time_partition["Equity Close"][i-1]
      df_time_partition["Equity Low"][i] = df_time_partition["Equity Close"][i-1]

      # used margin
      df_time_partition["Used Margin Open"][i] = df_time_partition["Used Margin Close"][i-1]
      df_time_partition["Used Margin Close"][i] = df_time_partition["Used Margin Close"][i-1]
      df_time_partition["Used Margin High"][i] = df_time_partition["Used Margin Close"][i-1]
      df_time_partition["Used Margin Low"][i] = df_time_partition["Used Margin Close"][i-1]

      # free margin
      df_time_partition["Free Margin Open"][i] = df_time_partition["Free Margin Close"][i-1]
      df_time_partition["Free Margin Close"][i] = df_time_partition["Free Margin Close"][i-1]
      df_time_partition["Free Margin High"][i] = df_time_partition["Free Margin Close"][i-1]
      df_time_partition["Free Margin Low"][i] = df_time_partition["Free Margin Close"][i-1]

      # % Difference from Balance
      df_time_partition["% Difference from Balance Open"][i] = df_time_partition["% Difference from Balance Close"][i-1]
      df_time_partition["% Difference from Balance Close"][i] = df_time_partition["% Difference from Balance Close"][i-1]
      df_time_partition["% Difference from Balance High"][i] = df_time_partition["% Difference from Balance Close"][i-1]
      df_time_partition["% Difference from Balance Low"][i] = df_time_partition["% Difference from Balance Close"][i-1]

      # % Difference from Equity
      df_time_partition["% Difference from Equity Open"][i] = df_time_partition["% Difference from Equity Close"][i-1]
      df_time_partition["% Difference from Equity Close"][i] = df_time_partition["% Difference from Equity Close"][i-1]
      df_time_partition["% Difference from Equity High"][i] = df_time_partition["% Difference from Equity Close"][i-1]
      df_time_partition["% Difference from Equity Low"][i] = df_time_partition["% Difference from Equity Close"][i-1]



  else:
    # balance
    df_time_partition["Balance Open"][i] = time_partition_arraylist[i]["Balance"][time_partition_arraylist[i].index[0]]
    df_time_partition["Balance Close"][i] = time_partition_arraylist[i]["Balance"][time_partition_arraylist[i].index[-1]]
    df_time_partition["Balance High"][i] = time_partition_arraylist[i]["Balance"].max()
    df_time_partition["Balance Low"][i] = time_partition_arraylist[i]["Balance"].min()

    # equity
    df_time_partition["Equity Open"][i] = time_partition_arraylist[i]["Equity"][time_partition_arraylist[i].index[0]]
    df_time_partition["Equity Close"][i] = time_partition_arraylist[i]["Equity"][time_partition_arraylist[i].index[-1]]
    df_time_partition["Equity High"][i] = time_partition_arraylist[i]["Equity"].max()
    df_time_partition["Equity Low"][i] = time_partition_arraylist[i]["Equity"].min()

    # used margin
    df_time_partition["Used Margin Open"][i] = time_partition_arraylist[i]["Used Margin"][time_partition_arraylist[i].index[0]]
    df_time_partition["Used Margin Close"][i] = time_partition_arraylist[i]["Used Margin"][time_partition_arraylist[i].index[-1]]
    df_time_partition["Used Margin High"][i] = time_partition_arraylist[i]["Used Margin"].max()
    df_time_partition["Used Margin Low"][i] = time_partition_arraylist[i]["Used Margin"].min()

    # free margin
    df_time_partition["Free Margin Open"][i] = time_partition_arraylist[i]["Free Margin"][time_partition_arraylist[i].index[0]]
    df_time_partition["Free Margin Close"][i] = time_partition_arraylist[i]["Free Margin"][time_partition_arraylist[i].index[-1]]
    df_time_partition["Free Margin High"][i] = time_partition_arraylist[i]["Free Margin"].max()
    df_time_partition["Free Margin Low"][i] = time_partition_arraylist[i]["Free Margin"].min()

    # difference from balance
    df_time_partition["% Difference from Balance Open"][i] = time_partition_arraylist[i]["% Difference from Balance"][time_partition_arraylist[i].index[0]]
    df_time_partition["% Difference from Balance Close"][i] = time_partition_arraylist[i]["% Difference from Balance"][time_partition_arraylist[i].index[-1]]
    df_time_partition["% Difference from Balance High"][i] = time_partition_arraylist[i]["% Difference from Balance"].max()
    df_time_partition["% Difference from Balance Low"][i] = time_partition_arraylist[i]["% Difference from Balance"].min()

    # difference from equity
    df_time_partition["% Difference from Equity Open"][i] = time_partition_arraylist[i]["% Difference from Equity"][time_partition_arraylist[i].index[0]]
    df_time_partition["% Difference from Equity Close"][i] = time_partition_arraylist[i]["% Difference from Equity"][time_partition_arraylist[i].index[-1]]
    df_time_partition["% Difference from Equity High"][i] = time_partition_arraylist[i]["% Difference from Equity"].max()
    df_time_partition["% Difference from Equity Low"][i] = time_partition_arraylist[i]["% Difference from Equity"].min()

    ## CandleStick Chart Output
    df_balance = pd.DataFrame(index=range(len(time_partition_arraylist)))
df_equity = pd.DataFrame(index=range(len(time_partition_arraylist)))
df_dfb = pd.DataFrame(index=range(len(time_partition_arraylist)))
df_dfe = pd.DataFrame(index=range(len(time_partition_arraylist)))

# df_test["DateTime"] = df_time_partition["Date"] + (df_time_partition["Time"] - datetime(1900, 1, 1, 0, 0, 0))
df_balance["DateTime"] = df_time_partition["DateTime"]
df_balance["Open"] = df_time_partition["Balance Open"]
df_balance["Close"] = df_time_partition["Balance Close"]
df_balance["High"] = df_time_partition["Balance High"]
df_balance["Low"] = df_time_partition["Balance Low"]

df_equity["DateTime"] = df_time_partition["DateTime"]
df_equity["Open"] = df_time_partition["Equity Open"]
df_equity["Close"] = df_time_partition["Equity Close"]
df_equity["High"] = df_time_partition["Equity High"]
df_equity["Low"] = df_time_partition["Equity Low"]

df_dfb["DateTime"] = df_time_partition["DateTime"]
df_dfb["Open"] = df_time_partition["% Difference from Balance Open"]*100
df_dfb["Close"] = df_time_partition["% Difference from Balance Close"]*100
df_dfb["High"] = df_time_partition["% Difference from Balance High"]*100
df_dfb["Low"] = df_time_partition["% Difference from Balance Low"]*100

df_dfe["DateTime"] = df_time_partition["DateTime"]
df_dfe["Open"] = df_time_partition["% Difference from Equity Open"]*100
df_dfe["Close"] = df_time_partition["% Difference from Equity Close"]*100
df_dfe["High"] = df_time_partition["% Difference from Equity High"]*100
df_dfe["Low"] = df_time_partition["% Difference from Equity Low"]*100

df_balance.set_index("DateTime", inplace=True)
df_equity.set_index("DateTime", inplace=True)
df_dfb.set_index("DateTime", inplace=True)
df_dfe.set_index("DateTime", inplace=True)

mpf.plot(df_balance, type='candle', style='yahoo', tight_layout=True, title = output_title+ ' (Balance)', ylabel="Price/USD", figratio=(20,10), savefig=output_title+ ' (Balance)')
mpf.plot(df_equity, type='candle', style='yahoo', tight_layout=True, title = output_title+ ' (Equity)', ylabel="Price/USD", figratio=(20,10), savefig=output_title+ ' (Equity)')
mpf.plot(df_dfb, type='candle', style='yahoo', tight_layout=True, title = output_title+ ' (% Difference from Balance)', ylabel="% Change", figratio=(20,10), savefig=output_title+ ' (% Difference from Balance)')
mpf.plot(df_dfe, type='candle', style='yahoo', tight_layout=True, title = output_title+ ' (% Difference from Equity)', ylabel="% Change", figratio=(20,10), savefig=output_title+ ' (% Difference from Equity)')


plt.show()

df_time_partition.to_csv(output_filename_candlestick, index=False)

# --------------------------------------------

# Part 3: Combine Images in 2 x 2 Grid

# Set the directory containing the PNG files
input_directory = ""

# Set the output file name and path
# output_file = "/content/combined.png"
output_file = output_title+".png"

# List all PNG files in the input directory
# only png files have ").png" to
png_files = [f for f in os.listdir(input_directory) if (f.startswith(output_title) and f.endswith(").png"))]

# Create a list to store images
images = []

# Loop through each PNG file and append it to the images list
for png_file in png_files:
    file_path = os.path.join(input_directory, png_file)
    img = Image.open(file_path)
    images.append(img)

x_offset = images[0].width
y_offset = images[0].height

# Combine the images in (2 x 2) array
combined_image = Image.new("RGB", (x_offset*2, y_offset*2))

# this numbering is done in a certain way so that
# balance and equity and dfb, dfe appears a certain way
combined_image.paste(images[0], (0,0))
combined_image.paste(images[3], (x_offset, 0))
combined_image.paste(images[2], (0, y_offset))
combined_image.paste(images[1], (x_offset, y_offset))

# Save the combined image
combined_image.save(output_file)

# Delete individual files
for png_file in png_files:
    file_path = os.path.join(input_directory, png_file)
    os.remove(file_path)
