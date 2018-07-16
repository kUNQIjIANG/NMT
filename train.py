import tensorflow as tf 
import os
import trainer
import pickle
from trainer import Trainer
import random
import numpy as np
from nltk import word_tokenize
from data import DataFlow 

hid_units = 100
batch_size = 32 
epochs = 5
c_size = 2
beam_width = 5
embed_size = 100
sos_id = 0
eos_id = 1
vocab_size = 20000
max_len = 15

with tf.Session() as sess:

    word_embeds = tf.get_variable("word_embeds",[vocab_size, embed_size])

    trainer = Trainer(hid_units, batch_size, vocab_size, embed_size, c_size, word_embeds, sos_id, eos_id,beam_width)
    data = DataFlow(vocab_size, max_len, batch_size)
    iterator = data.load()
    if os.path.isdir('saved_oop'):
        trainer.encoder.load(sess)
        trainer.generator.load(sess)
        trainer.discriminator.load(sess)  
    else:
        sess.run(tf.global_variables_initializer())
        print("global initialing")
    step = 1
    for epoch in range(epochs):
        sess.run(iterator.initializer)
        while True:
            try:
                enc_inp, dec_inp, dec_tar, enc_label = sess.run(iterator.get_next())
                
                enc_len, dec_len = sess.run([tf.count_nonzero(enc_inp, axis = 1),
                							 tf.count_nonzero(dec_inp, axis = 1)])
                
                enc_label = sess.run(tf.one_hot(enc_label, depth = 2))
                
                given_c = np.concatenate((np.zeros([batch_size,1]),np.ones([batch_size,1])),axis=1)

                gen_sen, gen_label = trainer.wakeTrain(sess, enc_inp, enc_len, dec_inp, dec_len, dec_tar,step)
                
                con_sen = np.concatenate((enc_inp, gen_sen[:,:-1]), axis = 0)
                con_lab = np.concatenate((enc_label, gen_label), axis = 0)
                con_len = np.concatenate((enc_len,enc_len), axis = 0)
                trainer.sleepTrain(sess, con_sen, con_len, con_lab)
                #inf_ids = trainer.inference(sess,enc_inp, enc_len,given_c)

                # trianing output
                if step % 10 == 0:
                    for tr, truth in zip(gen_sen, dec_tar):
                        print("truth: " + ' '.join([data.id2word[id] for id in truth]))
                        print("train: " + ' '.join([data.id2word[id] for id in tr])) 
                """
                # inference output 
                if step % 1 == 0:
                    for inf, truth in zip(inf_ids, dec_tar):
                        print("truth: " + ' '.join([data.id2word[id] for id in truth]))
                        print("inf: " + ' '.join([data.id2word[id] for id in inf])) 
                """
                step += 1
            except tf.errors.OutOfRangeError:
                break
