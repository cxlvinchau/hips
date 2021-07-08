import unittest
import numpy as np
import itertools

from hips import HIPSArray


class HIPSArrayTest(unittest.TestCase):

    def setUp(self) -> None:
        self.rng = np.random.default_rng()

    def test_addition(self):
        for i, j in itertools.product(range(1, 50), range(1, 50)):
            arr1 = self.rng.random(size=(i,j))
            arr2 = self.rng.random(size=(i,j))
            self.assertTrue(np.array_equal((HIPSArray(arr1) + HIPSArray(arr2)).array, arr1 + arr2))

    def test_subtraction(self):
        for i, j in itertools.product(range(1, 50), range(1, 50)):
            arr1 = self.rng.random(size=(i, j))
            arr2 = self.rng.random(size=(i, j))
            self.assertTrue(np.array_equal((HIPSArray(arr1) - HIPSArray(arr2)).array, arr1 - arr2))

    def test_multiplication(self):
        for i, j in itertools.product(range(1, 50), range(1, 50)):
            arr1 = self.rng.random(size=(i, j))
            scalar = self.rng.random(1)[0]
            self.assertTrue(np.array_equal((HIPSArray(arr1) * scalar).array, scalar * arr1))

    def test_numpy(self):
        # Creating a 4x4 identity matrix
        HIPSArray(np.identity(4))
        # Creating a 2x3 matrix with zeros
        HIPSArray(np.zeros((2, 3)))
        # A simple numpy array
        HIPSArray(np.array([1, 2, 3]))


if __name__ == '__main__':
    unittest.main()
