#!/usr/bin/env python3

'''
task 0 to 4
'''

import redis
import uuid
from typing import Union, Callable, Optional
from functools import wraps


class Cache:
    '''
    Class for implementing a Cache
    '''
    """ Familiarize yourself with the INCR command and its python equivalent.

    In this task, we will implement a system to count how many times methods of the Cache class are called.

    Above Cache define a count_calls decorator that takes a single method Callable argument and returns a Callable.

    As a key, use the qualified name of method using the __qualname__ dunder method.

    Create and return function that increments the count for that key every time the method is called and returns the value returned by the original method.

    Remember that the first argument of the wrapped function will be self which is the instance itself, which lets you access the Redis instance.

    Protip: when defining a decorator it is useful to use functool.wraps to conserve the original function’s name, docstring, etc. Make sure you use it as described here.

    Decorate Cache.store with count_calls. """

    @staticmethod
    def count_calls(fn: Callable) -> Callable:
        '''
        Count calls decorator
        '''
        @wraps(fn)
        def wrapper(self, *args, **kwargs):
            '''
            Wrapper function
            '''
            key = fn.__qualname__
            self._redis.incr(key)
            return fn(self, *args, **kwargs)
        return wrapper

    """
    In this task, we will define a call_history decorator to store the history of inputs and outputs for a particular function.

    Everytime the original function will be called, we will add its input parameters to one list in redis, and store its output into another list.

    In call_history, use the decorated function’s qualified name and append ":inputs" and ":outputs" to create input and output list keys, respectively.

    call_history has a single parameter named method that is a Callable and returns a Callable.

    In the new function that the decorator will return, use rpush to append the input arguments. Remember that Redis can only store strings, bytes and numbers. Therefore, we can simply use str(args) to normalize. We can ignore potential kwargs for now.

    Execute the wrapped function to retrieve the output. Store the output using rpush in the "...:outputs" list, then return the output.

    Decorate Cache.store with call_history.
    """
    @staticmethod
    def call_history(method: Callable) -> Callable:
        '''
        Store history of inputs and outputs
        '''
        @wraps(method)
        def wrapper(self, *args, **kwargs):
            '''
            Wrapper function
            '''
            key = method.__qualname__
            self._redis.rpush(key + ":inputs", str(args))
            output = method(self, *args, **kwargs)
            self._redis.rpush(key + ":outputs", output)
            return output
        return wrapper

    def __init__(self):
        '''
        Initialize class instance
        '''
        self._redis = redis.Redis()
        self._redis.flushdb()
    
    def store(self, data: Union[str, bytes, int, float]) -> str:
        '''
        Store data in Redis instance
        '''
        key = str(uuid.uuid4())
        self._redis.set(key, data)
        return key
    
    def get(self, key: str, fn: Optional[Callable] = None) -> Union[str, bytes, int, float]:
        '''
        Get data from Redis instance
        '''
        if fn:
            return fn(self._redis.get(key))
        else:
            return self._redis.get(key)
    
    def get_str(self, key: str) -> str:
        '''
        Convert bytes to str
        '''
        return self.get(key, str)
    
    def get_int(self, key: str) -> int:
        '''
        Convert bytes to int
        '''
        return self.get(key, int)
    
    """
    In this tasks, we will implement a replay function to display the history of calls of a particular function.
    Use keys generated in previous tasks to generate the following output:
    """
    def replay(self):
        '''
        Display history of calls of a particular function
        '''
        keys = self._redis.keys("*")
        for key in keys:
            if b":inputs" in key:
                key = key.decode("utf-8")
                method = key.split(":")[0]
                inputs = self._redis.lrange(key, 0, -1)
                outputs = self._redis.lrange(method + ":outputs", 0, -1)
                print("{} was called {} times:".format(method, len(inputs)))
                for i, o in zip(inputs, outputs):
                    print("{}(*{}) -> {}".format(method, i.decode("utf-8"), o.decode("utf-8")))
    

    """
    In this tasks, we will implement a get_page function (prototype: def get_page(url: str) -> str:). The core of the function is very simple. It uses the requests module to obtain the HTML content of a particular URL and returns it.

    Start in a new file named web.py and do not reuse the code written in exercise.py.

    Inside get_page track how many times a particular URL was accessed in the key "count:{url}" and cache the result with an expiration time of 10 seconds.

    Tip: Use http://slowwly.robertomurray.co.uk to simulate a slow response and test your caching.

    Bonus: implement this use case with decorators.
    """
    @Cache.count_calls
    @Cache.call_history
    def get_page(self, url: str) -> str:
        '''
        Get page from url
        '''
        import requests
        page = requests.get(url)
        return page.text