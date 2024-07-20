#!/usr/bin/python3
""" Test the code in web.py """
import redis
import time


get_page = __import__('web').get_page
client = redis.Redis()

url = "http://www.google.com"

print(f"Number of request to {url}: {client.get('count:{}'.format(url))}")
get_page(url)
print(f"Number of request to {url}: {client.get('count:{}'.format(url))}")
get_page(url)
print(f"Number of request to {url}: {client.get('count:{}'.format(url))}")

for i in range(10):
    print(f"Time to Live: {client.ttl('count:{}'.format(url))}")
    time.sleep(1)

print(f"Number of request to {url}: {client.get('count:{}'.format(url))}")
