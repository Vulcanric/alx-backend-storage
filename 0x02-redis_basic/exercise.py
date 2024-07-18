#!/usr/bin/env python3
""" Implement a Cache class for storing data """
import redis
import uuid  # For Key generation
from typing import Union, Callable, Any


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

    def store(self, data: Union[str, bytes, int, float]) -> str:
        """
        Stores the input data with a generated key.

        Args:
            data (str | bytes | int | float): Data to be stored

        Returns:
            key of data
        """
        data_key = str(uuid.uuid4())  # Generate key
        self._redis.set(data_key, data)  # Store data
        return data_key

    def get(self, key: str, fn: Callable[..., Any]) -> Any:
        """
        Retrieves a data from redis database by it's key. Calls a function
        on the data to convert it to a desired state.

        Args:
            key: The key to find value by
            fn: callable to convert data

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
