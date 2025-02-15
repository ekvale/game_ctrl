from django.http import JsonResponse
from django.db import connections
from django.db.utils import OperationalError
from redis import Redis
from redis.exceptions import RedisError
import logging

logger = logging.getLogger('game_ctrl.health')

def health_check(request):
    checks = {
        'database': check_database(),
        'redis': check_redis(),
    }
    status = 200 if all(checks.values()) else 503
    return JsonResponse({'status': checks}, status=status)

def check_database():
    try:
        connections['default'].cursor()
        return True
    except OperationalError:
        return False

def check_redis():
    try:
        redis = Redis.from_url(settings.CACHES['default']['LOCATION'])
        redis.ping()
        return True
    except RedisError:
        return False 