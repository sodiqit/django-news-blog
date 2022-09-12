import re


def to_snake_case(name):
    name = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', name)
    name = re.sub('__([A-Z])', r'_\1', name)
    name = re.sub('([a-z0-9])([A-Z])', r'\1_\2', name)
    return name.lower()


class Container:
    def override(self, dependency, new_dependency):
        self[to_snake_case(dependency.__name__)] = new_dependency()

    def add_dependency(self, dependency):
        self[to_snake_case(dependency.__name__)] = dependency()

    def add_dependency_without_instance(self, dependency):
        self[to_snake_case(dependency.__name__)] = dependency

    def __getitem__(self, key):
        return getattr(self, key)

    def __setitem__(self, key, value):
        return setattr(self, key, value)


containers_map: dict[str, Container] = {}


def inject(name: str, *args, without_instance: bool = False):
    if not name or type(name).__name__ != 'str':
        raise ValueError('Provide name for inject')

    def inner(fn):
        container = get_container(name)
        if container is None:
            container = Container()
            containers_map[name] = container
        
        for dep in args:
            if without_instance:
                container.add_dependency_without_instance(dep)
            else:
                container.add_dependency(dep)

        def inner1(self, *args, **kwargs):
            new_args = {**kwargs, 'container': container}
            fn(self, *args, **new_args)

        return inner1

    return inner


def get_container(name: str) -> Container | None:
    return containers_map.get(name)
