import collections


import numpy as np


from keras.preprocessing.text import Tokenizer
from keras.preprocessing.sequence import pad_sequences
from keras.models import Model
from keras.layers import GRU, Input, Dense, TimeDistributed, Activation, RepeatVector, Bidirectional, LSTM
from keras.layers.embeddings import Embedding
from tensorflow.keras.optimizers import Adam
from keras.losses import sparse_categorical_crossentropy
from tensorflow.python.client import device_lib
print(device_lib.list_local_devices())



print('Dataset Loaded')

def tokenize(x):
    """
    Tokenize x
    :param x: List of sentences/strings to be tokenized
    :return: Tuple of (tokenized x data, tokenizer used to tokenize x)
    """
    tokenizer  = Tokenizer(num_words=None, char_level=False)
    tokenizer.fit_on_texts(x)
    sequences = tokenizer.texts_to_sequences(x)
    
    return sequences, tokenizer

def preprocess(x, y):
    """
    Preprocess x and y
    :param x: Feature List of sentences
    :param y: Label List of sentences
    :return: Tuple of (Preprocessed x, Preprocessed y, x tokenizer, y tokenizer)
    """
    preprocess_x, x_tk = tokenize(x)
    preprocess_y, y_tk = tokenize(y)

    preprocess_x = pad(preprocess_x)
    preprocess_y = pad(preprocess_y)

    # Keras's sparse_categorical_crossentropy function requires the labels to be in 3 dimensions
    #preprocess_y = preprocess_y.reshape(*preprocess_y.shape, 1)

    return preprocess_x, preprocess_y, x_tk, y_tk

def pad(x, length=None):
    """
    Pad x
    :param x: List of sequences.
    :param length: Length to pad the sequence to.  If None, use length of longest sequence in x.
    :return: Padded numpy array of sequences
    """
    padded_sequences = pad_sequences(x, maxlen=length, padding="post", truncating="post")
    return padded_sequences

def lstm_model():
    """
    Build and train an encoder-decoder model on x and y
    :param input_shape: Tuple of input shape
    :param output_sequence_length: Length of output sequence
    :param english_vocab_size: Number of unique English words in the dataset
    :param french_vocab_size: Number of unique French words in the dataset
    :return: Keras model built, but not trained
    """

    # Load English data
    a = open('comments.txt',"r")
    # Load French data
    b = open('polls.txt',"r")
    comments = a.readlines()[0:17]
    polls = b.readlines()[0:17]
    comment_tokens=[]
    poll_tokens=[]
    for i in range(0,len(comments)):
        comments[i].replace("\n","")
        for k in comments[i].split(" "):
            if k not in comment_tokens:
                comment_tokens.append(k)
        
        polls[i].replace("\n","")
        for j in polls[i].split(" "):
            if j not in poll_tokens:
                poll_tokens.append(j)
    comments,polls,comment_tokenizer,poll_tokenizer=preprocess(comments,polls)
    learning_rate = 0.01
    latent_dim = 256
    
    encoder_inputs = Input(shape=(None, len(comment_tokens)+1))
    encoder = LSTM(latent_dim, return_state=True)
    encoder_outputs, state_h, state_c = encoder(encoder_inputs)
    # We discard `encoder_outputs` and only keep the states.
    encoder_states = [state_h, state_c]

    # Set up the decoder, using `encoder_states` as initial state.
    decoder_inputs = Input(shape=(None, len(poll_tokens)+1))
    # We set up our decoder to return full output sequences,
    # and to return internal states as well. We don't use the
    # return states in the training model, but we will use them in inference.
    decoder_lstm = LSTM(latent_dim, return_sequences=True, return_state=True)
    decoder_outputs, _, _ = decoder_lstm(decoder_inputs,
                                        initial_state=encoder_states)
    decoder_dense = Dense( len(poll_tokens)+1, activation='softmax')
    decoder_outputs = decoder_dense(decoder_outputs)

    # Define the model that will turn
    # `encoder_input_data` & `decoder_input_data` into `decoder_target_data`
    model = Model([encoder_inputs, decoder_inputs], decoder_outputs)
    model.compile(loss=sparse_categorical_crossentropy,
                 optimizer=Adam(learning_rate),
                 metrics=["accuracy"])
    return model, comments, polls

lstm_rnn_model, comments, polls= lstm_model()
lstm_rnn_model.summary()
print()
print(comments)
print()
print()
print(polls)
lstm_rnn_model.fit(comments, polls,  batch_size=1024, epochs=10, validation_split=0.2)