# The code below was copied from (https://www.tensorflow.org/tutorials/quickstart/beginner) for the purpose of an example.

import tensorflow as tf
import config

# load and normalize data
(x_train, y_train), (x_test, y_test) = tf.keras.datasets.mnist.load_data()
x_train, x_test = x_train / 255.0, x_test / 255.0

# define neural network architecture
model = tf.keras.models.Sequential([
  tf.keras.layers.Flatten(input_shape=(28, 28)),
  tf.keras.layers.Dense(config.get('LAYER1_NEURONS', 128), activation='relu'),
  tf.keras.layers.Dropout(config.get('DROPOUT', 0.2)),
  tf.keras.layers.Dense(10)
])

# define loss and compile the model
loss_fn = tf.keras.losses.SparseCategoricalCrossentropy(from_logits=True)
model.compile(optimizer='adam', loss=loss_fn, metrics=['accuracy'])

model.fit(x_train, y_train, epochs=5)
model.evaluate(x_test,  y_test, verbose=2)