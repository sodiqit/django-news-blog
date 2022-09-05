from functools import reduce
from typing import Any, Callable


def curry(num_args: int):
    def decorator(fn):
        def init(*args, **kwargs):
            def call(*more_args, **more_kwargs):
                all_args = args + more_args
                all_kwargs = dict(**kwargs, **more_kwargs)
                if len(all_args) + len(all_kwargs) >= num_args:
                    return fn(*all_args, **all_kwargs)
                else:
                    return init(*all_args, **all_kwargs)

            return call
        return init()
    return decorator

def pipe(initial_value: Any, *args: Callable):
    return reduce(lambda x, y: y(x), args, initial_value)