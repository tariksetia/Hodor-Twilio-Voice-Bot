import redis

myHostname = "hodor.redis.cache.windows.net"
myPassword = "fGivnomcqYdiLOQeaJJS1T7CeD2jNKt4bNR4XDh7a0Q="
redis_store = redis.StrictRedis(host=myHostname, port=6380,password=myPassword,ssl=True)