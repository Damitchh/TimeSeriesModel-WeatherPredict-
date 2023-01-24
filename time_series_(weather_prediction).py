# -*- coding: utf-8 -*-
"""Time Series (Weather Prediction).ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1zrjGa7l4CdeV5rw2UFihp95bdBGIJwY4
"""

#Get data sebanyak 10000 dari dataset
import pandas as pd
df = pd.read_csv('https://query.data.world/s/tu7xkafdc4jbuzmuh5zxqaeshwj7sv', encoding= 'unicode_escape')
df.head()

#Drop Column yang tidak dibutuhkan
df.drop(['City','Latitude','Longitude'], axis=1, inplace=True)
df

#Get Dataset dari tahun 1900 hingga 2013

df['dt'] = pd.to_datetime(df['dt'])  
get_data = (df['dt'] > '1900-01-01') & (df['dt'] <= '2013-09-01')
df.loc[get_data]

df = df.loc[get_data]
df

#Data yang akan digunakan adalah data dari negara Syria

df = df.loc[df['Country'].isin(['India'])]
df

#Reset Index dan drop kolom country

df.drop(['Country'], axis=1, inplace=True)
df.reset_index(drop=True)

#melakukan cleaning data terhadap nilai null

df.dropna(subset=['AverageTemperature'],inplace=True)
df.dropna(subset=['AverageTemperatureUncertainty'],inplace=True)
df.isnull().sum()

import matplotlib.pyplot as plt
#data exploratory

df_plot = df
df_plot[df_plot.columns.to_list()].plot(subplots=True, figsize=(15, 9))
plt.show()

#Data Exploratory
import numpy as np


dates = df['dt'].values
temp = df['AverageTemperature'].values

dates = np.array(dates)
temp = np.array(temp)

plt.figure(figsize=(10,4))
plt.plot(dates, temp)

plt.title('Average Temperature', fontsize = 10)
plt.ylabel('Temperature')
plt.xlabel('Datetime')

df.dtypes

#Membagi dataset dan data latih dengan split 20%
from sklearn.model_selection import train_test_split


x_train, x_valid, y_train, y_valid = train_test_split(temp, dates, train_size=0.8, test_size = 0.2, shuffle = False )
print('Total Data Train : ',len(x_train))
print('Total Data Validation : ',len(x_valid))

import tensorflow as tf
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM,Dense,Bidirectional,Dropout

def windowed_dataset(series, window_size, batch_size, shuffle_buffer):
  series = tf.expand_dims(series, axis=-1)
  ds = tf.data.Dataset.from_tensor_slices(series)
  ds = ds.window(window_size + 1, shift=1, drop_remainder = True)
  ds = ds.flat_map(lambda w: w.batch(window_size + 1))
  ds = ds.shuffle(shuffle_buffer)
  ds = ds.map(lambda w: (w[:-1], w[-1:]))
  return ds.batch(batch_size).prefetch(1)

#Pemodelan dengan Sequential

tf.keras.backend.set_floatx('float64')

train_set = windowed_dataset(x_train, window_size=64, batch_size=200, shuffle_buffer=1000)
val_set = windowed_dataset(x_valid, window_size=64, batch_size=200, shuffle_buffer=1000)

model = Sequential([
    Bidirectional(LSTM(60, return_sequences=True)),
    Bidirectional(LSTM(60)),
    Dense(30, activation="relu"),
    Dense(10, activation="relu"),
    Dense(1),
])

#Menentukan nilai MEA 

Mae = (df['AverageTemperature'].max() - df['AverageTemperature'].min()) * 10/100
print(Mae)

#Menggunakan learning rate SGD untuk optimizer

optimizer = tf.keras.optimizers.SGD(lr=1.0000e-04, momentum=0.9)

model.compile(loss=tf.keras.losses.Huber(),
              optimizer=optimizer,
              metrics=["mae"])

history = model.fit(train_set, epochs=100, validation_data = val_set)

#Plot Accuracy
plt.plot(history.history['mae'])
plt.plot(history.history['val_mae'])
plt.title('Akurasi Model')
plt.ylabel('Mae')
plt.xlabel('epoch')
plt.legend(['Train', 'Val'], loc='upper left')
plt.show()

#Plot Loss
plt.plot(history.history['loss'])
plt.plot(history.history['val_loss'])
plt.title('Loss Model')
plt.ylabel('loss')
plt.xlabel('epoch')
plt.legend(['Train', 'Val'], loc='upper left')
plt.show()