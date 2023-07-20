from django.core.cache import caches

local_cache = caches['local-memory']


class CacheKey:
    # Redis Cache

    # Local (RAM) Cache
    TEMP_CLIENT_ID_KEY_FORMAT = 'client-id-mixin-{request_hash}-{instance_type}-{instance_id}'
