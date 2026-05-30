def add_numbers(a, b):
  if not isinstance(a, (int, float)) or not isinstance(b, (int, float)):
    raise ValueError("Both arguments must be numbers.")
  return a + b

def subtract_numbers(a, b):
  return a - b

def multiply_numbers(a, b):
  return a * b

def divide_numbers(a, b):
  if b == 0:
    raise ValueError("Cannot divide by zero.")
  return a / b
