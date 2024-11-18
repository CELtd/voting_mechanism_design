import numpy as np
import pandas as pd

class mapping:
    def __init__(self, max_val, min_val, length, total_sum):  
        self.max_val=max_val
        self.min_val=min_val
        self.length=length
        self.total_sum=total_sum
    def linear(self):
        x = np.linspace(self.max_val, self.min_val, self.length)
        x /= x.sum()
        x *= self.total_sum
        
        # if any values exceed the first_value, we need to adjust the values
        mm1 = x[0]
        mm2 = x[-1]
        if mm1 > self.max_val:
            delta = mm1 - self.max_val
        else:
            delta = 0
        x = np.linspace(mm1-delta, mm2+delta, self.length)
        x /= x.sum()
        x *= self.total_sum
    
        return x

    def logarithmic(self):
        # Create an array with exponentially decreasing values
        x = np.logspace(0, 1, self.length, base=10.0)
        x = self.max_val - (x - x.min()) / (x.max() - x.min()) * (self.max_val - self.min_val)
        
        # Normalize the array to sum up to total_sum
        x /= x.sum()
        x *= self.total_sum
        
        # Adjust if the maximum value exceeds self.max_val
        mm1 = x[0]
        if mm1 > self.max_val:
            delta = mm1 - self.max_val
        else:
            delta = 0
        
        # Adjust the array range based on delta and recreate the exponentially decreasing array
        x = np.logspace(0, 1, self.length, base=10.0)
        x = self.max_val - (x - x.min() + delta) / (x.max() - x.min()) * (self.max_val - self.min_val)
        
        # Normalize again to ensure the array sums up to total_sum
        x /= x.sum()
        x *= self.total_sum
        
        return x

    #exponential (negative exponential)

    def exponential(self):
        # Generate `length` points between 0 and 1
        x = np.linspace(0, 1, self.length)
        
        # Apply the exponential function y = e^(-4x)
        y = np.exp(-4 * x)
        
        # Normalize the curve so its range spans from max_val to min_val
        y = (y - y.min()) / (y.max() - y.min())  # Normalize to [0, 1]
        y = y * (self.max_val - self.min_val) + self.min_val  # Scale to [min_val, max_val]
        
        # Scale the curve so the sum matches total_sum
        y /= y.sum()  # Normalize to sum to 1
        y *= self.total_sum  # Scale to total_sum
        
        return y
        
   