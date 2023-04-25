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

    def get(self, key: str, fn: Optional[Callable]
            = None) -> Union[str, bytes, int, float]:
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
                    print("{}(*{}) -> {}".format(method,
                          i.decode("utf-8"), o.decode("utf-8")))
