from tensorflow.examples.tutorials.mnist import input_data
import tensorflow as tf 
import numpy as np
import matplotlib.pyplot as plt
from PIL import Image

sess = tf.InteractiveSession()

mnist = input_data.read_data_sets('MNIST_data', one_hot = True)

# weight initialization functions
def weight_variable(shape):
    initial = tf.truncated_normal(shape, stddev = 0.3)
    return tf.Variable(initial)

def bias_variable(shape):
    initial = tf.constant(0.1, shape=shape)
    return tf.Variable(initial)

# convolution and pool initialization functions
def conv2d(x, W):
	return tf.nn.conv2d(x, W, strides = [1, 1, 1, 1], padding = 'SAME')

def pool_2x2(x):
	return tf.nn.max_pool(x, ksize = [1, 2, 2, 1], strides = [1, 2, 2, 1], padding = 'SAME')

# random noise generator
def make_noise():
    initial = tf.constant(0.1, shape=[784])
    noise = tf.truncated_normal([784], stddev = 0.05)
    return noise+initial

# generate and save img to current folder
def gen_image(arr):
    two_d = np.reshape(arr, (28, 28))
    img = Image.fromarray(two_d, 'L')
    return img

# placeholders for input data
x = tf.placeholder(tf.float32, shape = [None, 784])
y_ = tf.placeholder(tf.float32, shape = [None, 10])

# reshape x tensor to be ready for convolution
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

# Fully connected layer
W_fc1 = weight_variable([7 * 7 * 64, 1024])
b_fc1 = bias_variable([1024])

h_pool2_flat = tf.reshape(h_pool2, [-1, 7 * 7 * 64])
h_fc1 = tf.nn.relu(tf.matmul(h_pool2_flat, W_fc1) + b_fc1)

# Dropouts
keep_prob = tf.placeholder("float")
h_fc1_drop = tf.nn.dropout(h_fc1, keep_prob)

# Output layer
W_fc2 = weight_variable([1024, 10])
b_fc2 = bias_variable([10])

y_conv = tf.nn.softmax(tf.matmul(h_fc1_drop, W_fc2) + b_fc2)

# train
#cross_entropy = -tf.reduce_sum(y_*tf.log(y_conv))
#train_step = tf.train.AdamOptimizer(1e-4).minimize(cross_entropy)

# check if y_conv == y_
correct_prediction = tf.equal(tf.argmax(y_conv, 1), tf.argmax(y_, 1))

# compute accuracy (1 or 0 when batch_size == 1)
accuracy = tf.reduce_mean(tf.cast(correct_prediction, tf.float32))

# Saver
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

# Save network
save_path = saver.save(sess, "save_1")
print("Model saved as: %s" % save_path)

'''
# Restore network
saver.restore(sess, "./save_1")
print("Model restored")

# Generate adversarial images
for i in range(10000):
    batch_xs, batch_ys = mnist.test.next_batch(1)
    noise = make_noise()
    acc = accuracy.eval(feed_dict = {x: [batch_xs[0]], y_: [batch_ys[0]], keep_prob: 1.0})
    if np.all(tf.one_hot(2,10).eval() == batch_ys[0]) and acc == 1:
        plt.imshow(batch_xs[0])
        #print(y_conv.eval(feed_dict = {x: [noise.eval() + batch_xs[0]], y_: [tf.one_hot(6, 10).eval()], keep_prob: 1.0}))
        bingo = accuracy.eval(feed_dict = {x: [noise.eval() + batch_xs[0]], y_: [tf.one_hot(6, 10).eval()], keep_prob: 1.0})
        if bingo == 1:
          print("BINGO")

# Test step
print("test accuracy %g" % accuracy.eval(feed_dict = {x: mnist.test.images, y_: mnist.test.labels, keep_prob: 1.0}))

