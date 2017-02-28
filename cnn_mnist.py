from tensorflow.examples.tutorials.mnist import input_data
import tensorflow as tf 
import numpy as np
import matplotlib.pyplot as plt
import random

sess = tf.InteractiveSession()

mnist = input_data.read_data_sets('MNIST_data', one_hot = True)

# initialize weight and bias
def weight_variable(shape):
    initial = tf.truncated_normal(shape, stddev = 0.3)
    return tf.Variable(initial)

def bias_variable(shape):
    initial = tf.constant(0.1, shape = shape)
    return tf.Variable(initial)

# transform convolution and pool functions
def conv2d(x, W):
    return tf.nn.conv2d(x, W, strides = [1, 1, 1, 1], padding = 'SAME')

def pool_2x2(x):
    return tf.nn.max_pool(x, ksize = [1, 2, 2, 1], strides = [1, 2, 2, 1], padding = 'SAME')

# generates random noise
def disrupt(x):
    initial = tf.constant(0.1, shape = [784])
    noise = initial + tf.truncated_normal([784], stddev = 0.05)
    noise = noise.eval()
    for j in range (784):
        # clipping for greyscale
        if noise[j] + x[j] < 0 or noise[j] + x[j] > 1:
            noise[j] = 0;
        num = random.randint(0, 9)
        if (num == 0 and x[j] >= 0.5):
            noise[j] = -x[j]
        if (num == 1 and x[j] <= 0.2):
            noise[j] = 1 - x[j]
    return noise

# transforms np.arr into 2-d color map
def gen_image(arr):
    plt.imshow(arr.reshape((28, 28)))

# placeholders for MNIST input data
x = tf.placeholder(tf.float32, shape = [None, 784])
y_ = tf.placeholder(tf.float32, shape = [None, 10])
x_image = tf.reshape(x, [-1, 28, 28,1])

# first convolution and max pool layers
W_conv1 = weight_variable([5, 5, 1, 32])
b_conv1 = bias_variable([32])
h_conv1 = tf.nn.relu(conv2d(x_image, W_conv1) + b_conv1)
h_pool1 = pool_2x2(h_conv1)

# second convolution and max pool layers
W_conv2 = weight_variable([5, 5, 32, 64])
b_conv2 = bias_variable([64])
h_conv2 = tf.nn.relu(conv2d(h_pool1, W_conv2) + b_conv2)
h_pool2 = pool_2x2(h_conv2)

# fully connected layer
W_fc1 = weight_variable([7 * 7 * 64, 1024])
b_fc1 = bias_variable([1024])
h_pool2_flat = tf.reshape(h_pool2, [-1, 7 * 7 * 64])
h_fc1 = tf.nn.relu(tf.matmul(h_pool2_flat, W_fc1) + b_fc1)

# dropouts
keep_prob = tf.placeholder("float")
h_fc1_drop = tf.nn.dropout(h_fc1, keep_prob)

# output layer
W_fc2 = weight_variable([1024, 10])
b_fc2 = bias_variable([10])
y_conv = tf.nn.softmax(tf.matmul(h_fc1_drop, W_fc2) + b_fc2)

# loss function
cross_entropy = -tf.reduce_sum(y_ * tf.log(y_conv))
train_step = tf.train.AdamOptimizer(1e-4).minimize(cross_entropy)
correct_prediction = tf.equal(tf.argmax(y_conv, 1), tf.argmax(y_, 1))
accuracy = tf.reduce_mean(tf.cast(correct_prediction, tf.float32))

# initialize saver
saver = tf.train.Saver(tf.global_variables())

'''
# Train steps 
sess.run(tf.global_variables_initializer())
for i in range(20000):
    batch = mnist.train.next_batch(50)
    if i % 100 == 0:
        train_accuracy = accuracy.eval(feed_dict = {x:batch[0], y_: batch[1], keep_prob: 1.0})
        print("step %d, training accuracy %g" % (i, train_accuracy))
    train_step.run(feed_dict = {x: batch[0], y_: batch[1], keep_prob: 0.5})

# Test step
print("test accuracy %g" % accuracy.eval(feed_dict = {x: mnist.test.images, y_: mnist.test.labels, keep_prob: 1.0}))

# Save network
save_path = saver.save(sess, "save_1")
print("Model saved as: %s" % save_path)

'''
# Restore network
saver.restore(sess, "./save_1")
print("Model restored")


it = 0
# Generate adversarial images
for i in range(10000):
    found = False
    batch_xs, batch_ys = mnist.test.next_batch(1)
    disruption = disrupt(batch_xs[0])
    acc = accuracy.eval(feed_dict = {x: [batch_xs[0]], y_: [batch_ys[0]], keep_prob: 1.0})
    if np.all(tf.one_hot(2,10).eval() == batch_ys[0]) and acc == 1:
        while (found != True):
            res = y_conv.eval(feed_dict = {x: [disruption + batch_xs[0]], keep_prob: 1.0})
            for k in range(1000)
                disruption[k] = disrupt(batch_xs[0])

            bingo = accuracy.eval(feed_dict = {x: [disruption + batch_xs[0]], y_: [tf.one_hot(6, 10).eval()], keep_prob: 1.0})
            print ("Sample: ", i, ". Softmax res: ", res)
            if bingo == 1:
                found = True
                gen_image(batchtch_xs[0])
                plt.savefig("%s_original.png" % it)
                gen_image(disruption)
                plt.savefig("%s_noise.png" % it)
                gen_image(disruption + batch_xs[0])
                plt.savefig("%s_combined.png" % it)
                print("BINGO")
                it += 1

