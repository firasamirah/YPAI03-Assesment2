# -*- coding: utf-8 -*-
"""Ecommerce Text Classification.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1K3FYelu9ol6UK-XKgAFbM8_hpQ9k84_h
"""

from google.colab import drive
drive.mount('/content/drive')

# 1. Import packages
import pandas as pd
import numpy as np
import tensorflow as tf
import matplotlib.pyplot as plt
import os

#2. Data loading
csv_dataset = os.path.join("/content/drive/MyDrive/ecommerceDataset.csv")
df = pd.read_csv(csv_dataset)

df = pd.read_csv(csv_dataset, names=['label', 'text'], header=0)

#3. Data inspection
print(df.info())
print("-"*20)
print(df.describe())
print("-"*20)
print(df.isna().sum())
print("-"*20)
print(df.duplicated().sum())

#4. Data cleaning
df.drop_duplicates()
print(df.info())

df.dropna(inplace=True)

df.isnull().sum()

#5. The review is the feature, the sentiment is the label
feature = df['text'].values
label = df['label'].values

#5. Convert label into integers using LabelEncoder
from sklearn.preprocessing import LabelEncoder
label_encoder = LabelEncoder()
label_processed = label_encoder.fit_transform(label)

#6. Data preprocessing
#import re
#def remove_unwanted_strings(review):
    #for index, data in enumerate(review):
        #review[index] = re.sub('<.*?>', ' ', data) 
        #review[index] = re.sub('[^a-zA-Z]',' ',data).lower().split()
    #return review
#feature_removed = remove_unwanted_strings(feature)

#7. Define some hyperparameters
vocab_size = 5000
embedding_dim = 64
max_length = 200
trunc_type = 'post'
padding_type = 'post'
oov_tok = '<OOV>'
training_portion = 0.8

## 8. Perform train test split
from sklearn.model_selection import train_test_split

X_train,X_test,y_train,y_test = train_test_split(feature,label_processed,train_size=training_portion,random_state=12345)

#9. Perform tokenization
from tensorflow import keras

tokenizer = keras.preprocessing.text.Tokenizer(num_words=vocab_size,split=" ",oov_token=oov_tok)
tokenizer.fit_on_texts(X_train)

word_index = tokenizer.word_index
print(dict(list(word_index.items())[0:10]))

X_train_tokens = tokenizer.texts_to_sequences(X_train)
X_test_tokens = tokenizer.texts_to_sequences(X_test)

#10. Perform padding and truncating
X_train_padded = keras.preprocessing.sequence.pad_sequences(X_train_tokens,maxlen=(max_length))
X_test_padded = keras.preprocessing.sequence.pad_sequences(X_test_tokens,maxlen=(max_length))

#13. Model development
#(A) Create the sequential model
model = keras.Sequential()
#(B) Create the input layer, in this case, it can be the embedding layer
model.add(keras.layers.Embedding(vocab_size,embedding_dim))
#(B) Create the bidirectional LSTM layer
model.add(keras.layers.Bidirectional(keras.layers.LSTM(embedding_dim)))
#(C) Classification layers
model.add(keras.layers.Dense(embedding_dim,activation='relu'))
model.add(tf.keras.layers.Dense(4, activation = 'softmax'))

model.summary()

#12. Model compilation
#Create a TensorBoard callback object for the usage of TensorBoard
import tensorflow as tf
import datetime
from tensorflow.keras import callbacks
from tensorflow.keras.callbacks import TensorBoard
base_log_path = r"tensorboard_logs\assessment_data"
log_path = os.path.join(base_log_path,datetime.datetime.now().strftime("%Y%m%d-%H%M%S"))
tb = callbacks.TensorBoard(log_path)

model.compile(optimizer='adam',loss='sparse_categorical_crossentropy',metrics=['accuracy'])

import numpy as np
from sklearn.metrics import f1_score

# Train the model
history = model.fit(X_train_padded, y_train, validation_data=(X_test_padded, y_test), epochs=5, batch_size=64, callbacks=[tb])

#Make predictions on the test set
y_pred = model.predict(X_test_padded)
y_pred_labels = np.argmax(y_pred, axis=1)

#calculate the F1 score
f1 = f1_score(y_test, y_pred_labels, average='weighted')

#print the F1 score
print("F1 Score:", f1)

#14. Model evaluation
print(history.history.keys())

#Plot accuracy graphs
plt.figure()
plt.plot(history.history['accuracy'])
plt.plot(history.history['val_accuracy'])
plt.legend(["Train accuracy","Test accuracy"])
plt.show()

#15. Model deployment
test_string = ['Firas','Amirah']
test_string_tokens = tokenizer.texts_to_sequences(test_string)
test_string_padded = keras.preprocessing.sequence.pad_sequences(test_string_tokens,maxlen=(max_length))
y_pred = np.argmax(model.predict(test_string_padded), axis=1)

label_map =['Books','Clothing & Accessories','Electronics','Household']
predicted_sentiment =[label_map[1] for i in y_pred]

PATH = os.getcwd()
print(PATH)

#Model save path
model_save_path = os.path.join(PATH,"saved_models")
keras.models.save_model(model,model_save_path)

model_loaded = keras.models.load_model(model_save_path)

model_path = os.path.join(model_save_path,"model.h5")
model.save(model_path)

import pickle

tokenizer_save_path= os.path.join(PATH,"tokenizer.pkl")
with open(tokenizer_save_path,'wb') as f:
  pickle.dump(tokenizer,f)

with open(tokenizer_save_path,'rb') as f:
  tokenizer_loaded = pickle.load(f)