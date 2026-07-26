from django.core.cache import cache
from core.cache import CacheNamespace


DEFAULT_TTL = 60*1


restaurant_list_cache = CacheNamespace(
    key_template="restaurants:list", 
    timeout=DEFAULT_TTL)

restaurant_menu_cache = CacheNamespace(
    key_template="restaurant:{restaurant_id}:menu", 
    timeout=DEFAULT_TTL)

restaurant_availability_cache = CacheNamespace(
    key_template="restaurant:{restaurant_id}:availability:{date}", 
    timeout=DEFAULT_TTL)

