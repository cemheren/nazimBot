from __future__ import absolute_import, division, print_function

import os
import pickle
from six.moves import urllib

import tflearn
import tensorflow as tf
from tflearn.data_utils import *

path = "nazim_input.txt"
char_idx_file = 'char_idx.pickle'

tf.logging.set_verbosity(tf.logging.ERROR)

maxlen = 100

char_idx = None
if os.path.isfile(char_idx_file):
  print('Loading previous char_idx')
  char_idx = pickle.load(open(char_idx_file, 'rb'))

X, Y, char_idx = \
    textfile_to_semi_redundant_sequences(path, seq_maxlen=maxlen, redun_step=3)

pickle.dump(char_idx, open(char_idx_file,'wb'))

g = tflearn.input_data([None, maxlen, len(char_idx)])
g = tflearn.lstm(g, 512, return_seq=True)
g = tflearn.dropout(g, 0.8)
g = tflearn.lstm(g, 512, return_seq=True)
g = tflearn.dropout(g, 0.8)
g = tflearn.lstm(g, 512)
g = tflearn.dropout(g, 0.8)
g = tflearn.fully_connected(g, len(char_idx), activation='softmax')
g = tflearn.regression(g, optimizer='adam', loss='categorical_crossentropy',
                       learning_rate=0.001)

m = tflearn.SequenceGenerator(g, dictionary=char_idx,
                              seq_maxlen=maxlen,
                              clip_gradients=5.0)

#m.save('shakespeare.model')

for i in range(10):
    seed = random_sequence_from_textfile(path, maxlen)
    m.fit(X, Y, validation_set=0.1, batch_size=512,
          n_epoch=100, run_id='nazim')
    print("-- TESTING...")
    print("-- Test with temperature of 1.0 --")
    print(m.generate(600, temperature=1.0, seq_seed=seed))
    print("-- Test with temperature of 0.5 --")
    print(m.generate(600, temperature=0.5, seq_seed=seed))

    m.save('nazim.final')
