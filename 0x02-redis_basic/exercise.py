#!/usr/bin/env python3
""" Implement a Cache class for storing data """
import redis
import uuid  # For Key generation
from typing import Callable, Any, Optional
from functools import wraps


# Read all definitions in Cache class before any definition outside
# Decorator function counts the number of calls on a method and stores count
def count_calls(method: Callable) -> Callable:
    mkey = method.__qualname__

    @wraps(method)
    def wrapper(self, *args, **kwargs):
        if self._redis.get(mkey):  # If called before
            self._redis.incr(mkey)  # Increment count
        else:  # If method hasn't been called before
            self._redis.set(mkey, 1)  # Start counting from 1

        return method(self, *args, **kwargs)
    return wrapper


# Decorator function stores method's inputs and outputs in respective lists
def call_history(method: Callable) -> Callable:
    inputs_list_key = f'{method.__qualname__}:inputs'
    outputs_list_key = f'{method.__qualname__}:outputs'

    @wraps(method)
    def wrapper(self, *args):
        self._redis.rpush(inputs_list_key, str(args))
        output = method(self, *args)
        self._redis.rpush(outputs_list_key, str(output))
        return output
    return wrapper


# Regular function that displays the history of calls of a specific function
def replay(func: Callable) -> None:
    """
    Displays calls history of a specific function decorated by `call_history`
    Prints history in the exact way function was called

    Arg:
        func(Callable): Function decorated by `call_history`

    Display Format:
        funcname(*arg, *kwargs)

    Returns: Nothing
    """
    fn = func.__qualname__
    local_redis = redis.Redis()

    # Retrieving calls history from database
    inputs = [_.decode() for _ in local_redis.lrange(f'{fn}:inputs', 0, -1)]
    outputs = [_.decode() for _ in local_redis.lrange(f'{fn}:outputs', 0, -1)]
    print(f"{fn} was called {len(inputs)} times:")

    # Display history data
    for input_, output in zip(inputs, outputs):
        print(f'{fn}(*{input_}) -> {output}')


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
    @call_history
    def store(self, data: Any) -> str:
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

    def get(self, key: str, fn: Optional[Callable] = None) -> Any:
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
