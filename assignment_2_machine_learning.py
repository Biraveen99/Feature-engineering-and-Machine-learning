# -*- coding: utf-8 -*-
"""Assignment 2 machine learning.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1dBf7R9Z0Q64eeeOiw6CHxDpNBXsm4Zeq

Assignment 2 by Biraveen, Ha, Yusuf, Shoaib
```
"""

import math
import numpy as np
from sklearn.preprocessing import MinMaxScaler
from keras.models import Sequential
from keras.layers import Dense, LSTM
import matplotlib.pyplot as plt
plt.style.use('fivethirtyeight')
import io
import pandas
from datetime import datetime
import requests
#workaround since the normal way dont work for some
class YahooData:
  def fetch(ticker, start, end):
    headers = {
        'User-Agent': 'workaround'
    }

    url = "https://query1.finance.yahoo.com/v7/finance/download/" + str(ticker)
    x = int(datetime.strptime(start, '%Y-%m-%d').strftime("%s"))
    y = int(datetime.strptime(end, '%Y-%m-%d').strftime("%s"))
    url += "?period1=" + str(x) + "&period2=" + str(y) + "&interval=1d&events=history&includeAdjustedClose=true"
    
    r = requests.get(url, headers=headers)
    pd = pandas.read_csv(io.StringIO(r.text), index_col=0, parse_dates=True)

    return pd


df = YahooData.fetch("TSLA", start="2000-01-01", end="2021-10-14")
print(df)

#just to print the number of columms and rows
df.shape 

#graph
#visualizing the closing price
plt.figure(figsize=(16,8))
plt.title('Close Price History')
plt.plot(df['Close'])
plt.xlabel('Date', fontsize = 18)
plt.ylabel('Close Price USD($)', fontsize= 18)
plt.show()


#creating new datafram eith just the "close"-colum
data = df.filter(['Close'])

#converting datafrma to numpy array 

dataset = data.values

#now to train our model based on rows
training_data_length = math.ceil(len(dataset)* .75) #using math function to round up 

training_data_length
#datascaling (important to do before giving it to a neural network)
scaler = MinMaxScaler(feature_range=(0,1))
scaled_data = scaler.fit_transform(dataset) #transform data based on min and max 

scaled_data #it does display everything if i dont run the code under. it will still run if there is code under it, but wont display it 

# Creating traning dataset and the scal(ing/ed) training dataset 
Data_trainer = scaled_data[0: training_data_length, :]

#now we split adta into x and y train
x_train = [] #independent traning vaiables
y_train = [] #target variables

#append the alst 60 values
for i in range(60,len(Data_trainer)):
  x_train.append(Data_trainer[i-60:i, 0])
  y_train.append(Data_trainer[i, 0])
  if i <= 61:
    print(x_train) #will contain the last 60 values
    print(y_train) #will contain the 61 value
    print()

#converting the x and y trian to numpy arrays to train the lstm model
x_train, y_train = np.array(x_train), np.array(y_train)

#reshaping the data from 2D to 3D
x_train = np.reshape(x_train, (x_train.shape[0],x_train.shape[1], 1))
x_train.shape

#building LSTM model
model = Sequential()
model.add(LSTM(50, return_sequences=True, input_shape =(x_train.shape[1],1)))
model.add(LSTM(50,return_sequences=False))
model.add(Dense(25))
model.add(Dense(1))

#compling model
model.compile(optimizer='adam', loss = 'mean_squared_error')

#model traning
model.fit(x_train,y_train, batch_size = 1, epochs=1)

#now we create testing dataset by creating a new arrat that contains scaled values.
test_data = scaled_data[training_data_length - 60: , : ]
#createing  data sets x_test and y_test
x_test= []
y_test = dataset[training_data_length:, :]
for i in range(60, len(test_data)):
  x_test.append(test_data[i-60:i, 0])

#convert data to numpt array
x_test = np.array(x_test)

#data reshaping
x_test = np.reshape(x_test, (x_test.shape[0], x_test.shape[1], 1))

#model prediction for x_test dataset
guess_predictions = model.predict(x_test)
guess_predictions = scaler.inverse_transform(guess_predictions) #kind of unscaling the values
#want predictions to contain same values as y_dataset

#model evaluation by (RMSE) this is for model accuracy (prediction percantage score)
RMSE = np.sqrt(np.mean (guess_predictions - y_test)**2 )
RMSE

#now we plot data 
train = data[:training_data_length]
validation = data[training_data_length:]
validation['guess_predictions'] = guess_predictions
#now we visualize data
plt.figure(figsize=(16,8))
plt.title('Model')
plt.xlabel('Data', fontsize = 18)
plt.ylabel('Close price in USD', fontsize=18)
plt.plot(train['Close'])
plt.plot(validation[['Close', 'guess_predictions']])
plt.legend(['train','validation', 'guess_predictions'], loc = 'lower right')
plt.show()
#blue = the training, orange=actual closing price, yellow = predctions

#here im going to show the preditcted price and actual price, 
validation

#trying to predict closing price for tesla stocks for 2021-11-14
#start by getting qoute
TSLA_quote = YahooData.fetch("TSLA", start="2000-01-01", end="2021-10-14")
#creating new datafram 
new_df = TSLA_quote.filter(['Close'])
#turning the last 60 day closing price values and converting the dataframe to an array
last_60_days = new_df[-60:].values
#datascaling to have vaues between 0 and 1
last60daysscaled= scaler.transform(last_60_days)
#creating empty list
x1_test = [] #not the same as the one i used before
#appending the last 60 days
x1_test.append(last60daysscaled)
#converting x1_test dataset to a numpy array 
x1_test = np.array(x1_test)
#data reshaping
x1_test = np.reshape(x1_test, (x1_test.shape[0], x1_test.shape[1], 1))
#getting the preditcted scale price
pred_price1 = model.predict(x1_test)
#undo scaling
pred_price1 = scaler.inverse_transform(pred_price1)
print(pred_price1) #will print the value on 2021-10-14

#showing the actual price
TSLA_quote1 = YahooData.fetch("TSLA", start="2021-10-14", end="2021-10-15")
print(TSLA_quote1['Close']) 
#as you can see i was of by x%