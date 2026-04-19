import numpy as np

x = np.array(12)
print(x.ndim)
print(x.shape)

x = np.array([12, 3, 6, 14])
print(x.ndim)
print(x.shape)
x = np.array([[12, 3, 6, 14], [1, 2, 3, 4]])
print(x.ndim)
print(x.shape)
x = np.array([[[12, 3, 6, 14], [1, 2, 3, 4]], [[1, 2, 3, 4], [5, 6, 7, 8]]])
print(x.ndim)
print(x.shape)
