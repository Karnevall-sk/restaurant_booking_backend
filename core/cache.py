from django.core.cache import cache

class CacheNamespace:
    def __init__(self, key_template: str, timeout: int = 900):
        self.key_template = key_template
        self.timeout = timeout

    def _make_key(self, **kwargs) -> str:
        return self.key_template.format(**kwargs)

    def get(self, **kwargs):
        
        return cache.get(self._make_key(**kwargs))

    def set(self, data, **kwargs):
        cache.set(self._make_key(**kwargs), data, timeout=self.timeout)

    def invalidate(self, **kwargs):
        print("aboba")
        cache.delete(self._make_key(**kwargs))

    def get_or_set(self, fetch_func, **kwargs):
        key = self._make_key(**kwargs)
        data = cache.get(key)
        print(f"got cache {data}")
        if data is None:
            data = fetch_func()
            cache.set(key, data, timeout=self.timeout)
        return data