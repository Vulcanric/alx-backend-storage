#!/usr/bin/env python3
""" Implements an expiring web cache and tracker """
import redis
import requests
from typing import Callable


# Decorator function used to track access to a particular url
def track_calls(func: Callable) -> Callable:
    """
    Tracks how many times a particular URL was accessed, storing
    its count to redis using the key `count:{url}`. This data lives
    for 10 seconds before expiring.
    """
    def wrapper(url: str) -> str:
        """
        Stores url access count into database
        """
        track_key = f'count:{url}'
        client = redis.Redis()

        if client.get(track_key):
            client.incr(track_key)
        else:
            client.set(track_key, 1)
            client.expire(track_key, 10)

        return func(url)
    return wrapper


@track_calls
def get_page(url: str) -> str:
    """
    get_page(url: str) -> str:
        Retrieves html content from the given url and returns it.

        Args:
            url (String): URL to fetch

        Returns:
            the html content fetched
    """
    response = requests.get(url=url)
    return response.text
