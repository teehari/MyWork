# -*- coding: utf-8 -*-

import pandas as pd
import numpy as np
import os
from keras.models import Sequential
from keras.layers import Dense, LSTM, InputLayer, Bidirectional, TimeDistributed, Activation
from keras.optimizers import Adam
import glob

train_vectors, train_tags = [], []

FEATURE_DIM = 1
MAX_LENGTH = 2000
allLabels = {}
#Input folder
inp = r"D:\Invoice Data Extraction\TAPP 3.0\taggedData\features\Hari"
removeCols = ['text', 'label', 'Folder', 'OriginalFile', 'SplitFile',
              'left_text', 'second_left_text', 'right_text',
              'second_right_text', 'top_text','left_top_text',
              'right_top_text', 'bottom_text', 'left_bottom_text',
              'right_bottom_text']

files = os.listdir(inp)
filepaths = glob.glob(os.path.join(inp,"Doc_88*"))

for fileind,filepath in enumerate(filepaths):

    print(filepath)
    inpfile = filepath
    df = pd.read_csv(inpfile,na_values = -1)
    df = df.fillna(-1)
    pages = list(df["page_num"].unique())

    for pageind, pagenum in enumerate(pages):
        if pageind == 1:
            filtered = df[df["page_num"] == pagenum]
            filtered = filtered.drop(["page_num"],axis = 1)
            filtered = filtered.sort_values(["token_id"])
            filtered = filtered.drop(["token_id"],axis = 1)
            labels = list(filtered["label"])
            filtered = filtered.drop(removeCols, axis = 1)
            filtered = filtered.astype(np.float64)
            FEATURE_DIM = filtered.shape[1]
            arr = np.array(filtered)
            if arr.shape[0] < MAX_LENGTH:
                diff = MAX_LENGTH - arr.shape[0]
                l = np.array([[-1] * arr.shape[1]] * diff)
                arr = np.vstack((arr,l))
                print(arr.shape)
                difflabels = ["-PAD-"] * diff
                labels.extend(difflabels)
            train_vectors.append(arr)
            train_tags.append(labels)
            for label in labels:
                label = label.lower().strip()
                lbls = label.split("_")
                if lbls > 1:
                    label = lbls[2]
                if label not in allLabels.keys():
                    allLabels[label] = len(allLabels.values()) + 1

train_tags_y = []

for s in train_tags:
    train_tags_y.append([allLabels[t] for t in s])


model = Sequential()
model.add(InputLayer(input_shape=(MAX_LENGTH,FEATURE_DIM)))
#model.add(Embedding(len(word2index), 128))
model.add(Bidirectional(LSTM(256,activation='tanh',
                             input_shape=(MAX_LENGTH,FEATURE_DIM),
                             recurrent_activation='sigmoid',
                             return_sequences=True,
                             dropout = 0.2)))
model.add(TimeDistributed(Dense(len(allLabels))))
model.add(Activation('softmax'))

model.compile(loss='categorical_crossentropy',
              optimizer=Adam(0.001),
              metrics=['accuracy'])

model.summary()

def to_categorical(sequences, categories):
    cat_sequences = []
    for s in sequences:
        cats = []

        for item in s:
            cats.append(np.zeros(categories))
            cats[-1][item - 1] = 1.0
        cat_sequences.append(cats)
    return np.array(cat_sequences)

cat_train_tags_y = to_categorical(train_tags_y, len(allLabels))

print("Modeling to be started")
train = np.array(train_vectors)
model.fit(np.array(train_vectors),
          to_categorical(train_tags_y, len(allLabels)),
          batch_size=128,
          epochs=1, validation_split=0.3)



