# Python concepts in Billify

This document contains both actual examples from our codebase (with links to implementations) and theoretical examples for illustration purposes.

## Enums
An enumeration is a set of symbolic names (members) bound to unique values:
- They are singletons (only one instance of each value exists)
- The enum class creates a fixed set of named constants
- You cannot create a 'traditional' instance of an enum class

Example from our codebase (implemented):
> Implementation: [backend/domain/models/value_objects.py](../../../backend/domain/models/value_objects.py)

```python
# Valid usage:
urgency1 = UrgencyLevel.OVERDUE
urgency2 = UrgencyLevel.CRITICAL

# Invalid usage:
invoice_urgency = UrgencyLevel()  # This will raise an error
```

## Decorators
A decorator is a function that wraps another function to add more functionality.

### @property decorator
Makes a method act like an attribute:
> Example from UrgencyLevel in [backend/domain/models/value_objects.py](../../../backend/domain/models/value_objects.py)

```python
# Instead of:
urgency.color_code()

# You can write:
urgency.color_code
```

### @classmethod decorator
Allows calling a method on the class itself rather than on an instance:
> Example from UrgencyLevel in [backend/domain/models/value_objects.py](../../../backend/domain/models/value_objects.py)

```python
# Can be called directly on the class:
UrgencyLevel.calculate_from_days(5)
```

## Class methods vs regular methods

### Regular methods
- Work with specific instances
- Receive the instance as the first argument (self)
- Need an instance to be called

### Class methods
- Work with the class itself
- Receive the class as the first argument (cls)
- Can access class state but not instance state

Theoretical example to illustrate the difference:
```python
class Car:
    # Class variable - shared by all instances
    total_cars = 0
    
    def __init__(self, color):
        self.color = color
        Car.total_cars += 1
    
    # Regular method - works with a specific car instance
    def paint_car(self, new_color):
        self.color = new_color
        return f"Car repainted to {new_color}"
    
    # Class method - works with the Car class itself
    @classmethod
    def get_total_cars(cls):
        return f"Total cars created: {cls.total_cars}"

# Usage examples:
my_car = Car("red")
your_car = Car("blue")

# Regular method needs an instance
my_car.paint_car("green")     # Works
Car.paint_car("green")        # Error!

# Class method can be called on class or instance
print(Car.get_total_cars())   # Works
print(my_car.get_total_cars()) # Also works
```

## ValueError
- One of python's built-in exceptions
- Used when an argument has the right type but the wrong value
- Different from TypeError (wrong type)

Example usage in defensive programming:
> Example from UrgencyLevel in [backend/domain/models/value_objects.py](../../../backend/domain/models/value_objects.py)

```python
def calculate_urgency(days):
    if days < 0:
        raise ValueError("Days cannot be negative")
    elif days >= 31:
        return UrgencyLevel.LOW
    # ... other conditions ...
    else:
        raise ValueError(f"Invalid days value: {days}")  # Defensive programming
```

### Why use ValueError?
1. Python can't know if all possible values are handled
2. Without a final return or raise, python would implicitly return None
3. This would conflict with type hints promising specific return types
4. It's part of defensive programming - handling "impossible" cases 