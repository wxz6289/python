import unittest

def average(data):
  return sum(data) / len(data)

class TestStatistic(unittest.TestCase):
  def test_average(self):
    # self.assertEqual(average([20, 30, 50]), 33.33)
    self.assertEqual(round(average([20, 30, 50])), 33)
    with self.assertRaises(ZeroDivisionError):
        average([])
    with self.assertRaises(TypeError):
        average(20, 30, 70)

unittest.main()
