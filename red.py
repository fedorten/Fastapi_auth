import redis

r = redis.Redis(host="localhost", port=6379)
print(r.set("foo", "bar"))
print(r.set("fof", "par"))
print(r.get("foo"))
print(r.get("fof"))
