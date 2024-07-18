#!/usr/bin/env python3
""" Implement a Cache class for storing data """
import redis
import uuid  # For Key generation
from typing import Union, Callable, Any, Optional
from functools import wraps


# Decorator function
def count_calls(method: Callable[..., Any]) -> Callable[..., Any]:
    """
    Counts the number of times a class method is called.
    Saves this count in the database with key as the
    method qualified name

    Args:
        method (Callable): Method to count number of calls on

    Returns:
        Wrapper function as `counter`
    """
    # @functool.wraps Prevents overwriting functions name and docstring
    # to that of wrapper
    @wraps(method)
    def wrapper(self, *args, **kwargs):
        """
        Counts the nummber of calls on method
        Returns: the actual output of method
        """
        # Use method's qualified name as a key to its count
        mkey = method.__qualname__

        if self._redis.get(mkey):  # If called before
            self._redis.incr(mkey)  # Increment count
        else:  # If method hasn't been called before
            self._redis.set(mkey, 1)  # Start counting from 1

        return method(self, *args, **kwargs)
    return wrapper


class Cache:
    """
    Class Cache:
        Template for cache instances

    Methods:
        __init__:
            Instantiates a Cache object, establishing a connection
            with redis server in the process, as a variable.
        store:
            Takes in a data in form of str, bytes, int, or float.
            Generates a unique key for this data and stores it in the
            database. It returns the key of the data
    """
    def __init__(self) -> None:
        """
        Instantiates a Cache object, creating an instance of the redis client

        Args: None
        Returns: None
        """
        # Establish a connection to redis via an instance
        self._redis = redis.Redis()
        self._redis.flushdb()  # Clear up the database

    @count_calls
    def store(self, data: Union[str, bytes, int, float]) -> str:
        """
        Stores the input data with a generated key.

        Args:
            data (String | bytes | int | float): Data to be stored
        Returns:
            key of data
        """
        data_key = str(uuid.uuid4())  # Generate key
        self._redis.set(data_key, data)  # Store data
        return data_key

    def get(self, key: str, fn: Optional[Callable[..., Any]] = None) -> Any:
        """
        Retrieves a data from redis database by it's key. Calls a function
        on the data to convert it to a desired state.

        Args:
            key (String): The key to find value by
            fn (Callable): callback function to convert data

        Returns:
            Converted data
        """
        data = self._redis.get(key)

        if data and fn is not None:
            data = fn(data)

        return data

    def get_str(self, key: str) -> str:
        """
        Retrieves a data from redis database as string.
        """
        return self.get(key, str)

    def get_int(self, key: str) -> int:
        """
        Retrieves a data from redis database as integer
        """
        return self.get(key, int)
