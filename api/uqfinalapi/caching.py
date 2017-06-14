"""
A series of helpers for caching values locally in Python and on DynamoDB
"""
import logging
import decimal

logger = logging.getLogger('api')


class CachedProperty(object):
    """
    A property which caches the return value
    """

    def __init__(self, f):
        self.f = f

    def __get__(self, instance, owner):
        if instance is None:
            return self
        value = self.f(instance)
        logger.warn("Calculating " + self.f.__name__)
        instance.__dict__[self.f.__name__] = value
        return value


cached_property = CachedProperty


class DynamoDBCachedProperty(CachedProperty):
    """
    A property which is cached and also saved to DynamoDB for future access without gaining it again from UQ
    """
    pass


dynamodb_cached_property = DynamoDBCachedProperty


class DynamoDBCachedObject(object):
    """
    Handles `DynamoCachedProperty` which appear on the object, adds helpers to read and write from DynamoDB
    """
    @property
    def partition_key(self):
        raise NotImplementedError

    @property
    def range_key(self):
        return None

    @classmethod
    def get_table_name(cls):
        raise NotImplementedError


def dynamodb_cast_types_to_python(obj):
    if isinstance(obj, list):
        for i in xrange(len(obj)):
            obj[i] = dynamodb_cast_types_to_python(obj[i])
        return obj
    elif isinstance(obj, dict):
        for k in obj.iterkeys():
            obj[k] = dynamodb_cast_types_to_python(obj[k])
        return obj
    elif isinstance(obj, decimal.Decimal):
        if obj % 1 == 0:
            return int(obj)
        else:
            return float(obj)
    else:
        return obj
