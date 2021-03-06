import math
from IPython  import display
from matplotlib import cm
from matplotlib import gridspec
from matplotlib import pyplot as plt
import numpy as np
import pandas as pd
from sklearn import metrics
import tensorflow as tf
from tensorflow.python.data import Dataset

tf.logging.set_verbosity(tf.logging.ERROR)
pd.options.display.max_rows = 10
pd.options.display.max_columns = 10
pd.options.display.float_format = '{:.1f}'.format
tf.reset_default_graph()

california_housing_dataset = pd.read_csv("https://storage.googleapis.com/mledu-datasets/california_housing_train.csv", sep=",",encoding="utf-8-sig")
california_housing_dataset = california_housing_dataset.reindex(np.random.permutation(california_housing_dataset.index))
california_housing_dataset /= 1000.0
# # print(california_housing_dataset)
# print(california_housing_dataset.describe())

#Building the model
#Define the feature room
my_feature = california_housing_dataset['total_rooms']
feature_columns = [tf.feature_column.numeric_column('total_rooms')]

#Define the target
targets = california_housing_dataset['median_house_value']

#Configure the linear expression
#We are optimizing as follows
my_optimizer = tf.train.GradientDescentOptimizer(learning_rate = 0.0000001)
my_optimizer = tf.contrib.estimator.clip_gradients_by_norm(my_optimizer, 5.0) #gradient clipping

linear_regressor = tf.estimator.LinearRegressor(
    feature_columns=feature_columns,
    optimizer=my_optimizer
)

#Define the input function
print("Hiiii")
def my_input_fn(features,targets,batch_size =1 ,shuffle = True, num_epochs =None):
    """Trains a linear regression model of one feature.

        Args:
          features: pandas DataFrame of features
          targets: pandas DataFrame of targets
          batch_size: Size of batches to be passed to the model
          shuffle: True or False. Whether to shuffle the data.
          num_epochs: Number of epochs for which data should be repeated. None = repeat indefinitely
        Returns:
          Tuple of (features, labels) for next data batch
        """
    #converts pandas data into  a dictionary of np arrays
    features =  {key: np.array(value) for key, value in dict(features).items()}
    print("Hi1")
    # print(features)
    # print(targets)
    # Construct a dataset, and configure batching/repeating.
    ds = Dataset.from_tensor_slices((features,targets)) #the limit is 2 gb
    print("Hi2")
    ds = ds.batch(batch_size).repeat(num_epochs)
    print("Hi3")
    #Shuffle the data, if specified
    if shuffle:
        ds = ds.shuffle(buffer_size = 1000)

    #return to the next batch of data
    features, labels = ds.make_one_shot_iterator().get_next()
    return features,labels

#Train the model
_ = linear_regressor.train(
    input_fn = lambda :my_input_fn(my_feature,targets),
     steps = 100
)



# 6. Evaluate the model

# Create an input function for predictions.
# Note: Since we're making just one prediction for each example, we don't
# need to repeat or shuffle the data here.
prediction_input_fn =lambda: my_input_fn(my_feature, targets, num_epochs=1, shuffle=False)

# Call predict() on the linear_regressor to make predictions.
predictions = linear_regressor.predict(input_fn=prediction_input_fn)

# Format predictions as a NumPy array, so we can calculate error metrics.
predictions = np.array([item['predictions'][0] for item in predictions])

# Print Mean Squared Error and Root Mean Squared Error.
mean_squared_error = metrics.mean_squared_error(predictions, targets)
root_mean_squared_error = math.sqrt(mean_squared_error)
print("Mean Squared Error (on training data): %0.3f" % mean_squared_error)
print("Root Mean Squared Error (on training data): %0.3f" % root_mean_squared_error)


