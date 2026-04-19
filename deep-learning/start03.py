from keras.datasets import mnist
(train_images, train_labels), (test_images, test_labels) = mnist.load_data()
print(train_images.shape)
print(train_images.ndim)
print(train_images.dtype)
print(train_images.size)
print(train_images.itemsize)
print(train_images.nbytes)
print(train_images.strides)
