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
import numpy as np
print(device_lib.list_local_devices())



print('Dataset Loaded')

def logits_to_text(logits, tokenizer):
    """
    Turn logits from a neural network into text using the tokenizer
    :param logits: Logits from a neural network
    :param tokenizer: Keras Tokenizer fit on the labels
    :return: String that represents the text of the logits
    """
    index_to_words = {id: word for word, id in tokenizer.word_index.items()}
    index_to_words[0] = '<PAD>'

    return ' '.join([index_to_words[prediction] for prediction in np.argmax(logits, 1)])



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
        comments[i]=comments[i].replace("\n","")
        comments[i]="START_ "+comments[i]+" _END"
        for k in comments[i].split(" "):
            if k not in comment_tokens:
                comment_tokens.append(k)
        
        polls[i]=polls[i].replace("\n","").replace("?","")
        polls[i]="START_ "+polls[i]+" _END"
        for j in polls[i].split(" "):
            if j not in poll_tokens:
                poll_tokens.append(j)
    
    comments,polls,comment_tokenizer,poll_tokenizer=preprocess(comments,polls)
    learning_rate = 0.01
    latent_dim = 256
    
    encoder_inputs = Input(shape=(len(comments[0]),1))
    encoder = encoder_gru = GRU(len(comments[0]))(encoder_inputs)
    encoder_outputs = Dense(latent_dim, activation="relu")(encoder_gru)
    decoder_inputs = RepeatVector(len(polls[0]))(encoder_outputs)
    decoder_gru = GRU(latent_dim, return_sequences=True)(decoder_inputs)
    decoder_output = TimeDistributed(Dense(len(comment_tokens)+1, activation="softmax"))(decoder_gru)

    # Define the model that will turn
    # `encoder_input_data` & `decoder_input_data` into `decoder_target_data`
    model = Model([encoder_inputs], decoder_output)
    model.compile(loss=sparse_categorical_crossentropy,
                 optimizer=Adam(learning_rate),
                 metrics=["accuracy"])
    return model, comments, polls, comment_tokenizer, poll_tokenizer

lstm_rnn_model, comments, polls, comment_tokenizer, poll_tokenizer= lstm_model()
lstm_rnn_model.summary()
"""
print()
print(comments)
print()
print()
print(polls)
"""
a=input()
if a=="t":
    lstm_rnn_model.fit(comments, polls,  batch_size=1024, epochs=1000, validation_split=0.2)
    lstm_rnn_model.save('model.h5')
else:
    lstm_rnn_model.load_weights("model.h5")
    print(logits_to_text(comments[0],comment_tokenizer))
    print(lstm_rnn_model.predict(np.reshape(comments[0],(102,1))).shape)