import redis

redis_server = 'ec2-52-35-109-64.us-west-2.compute.amazonaws.com'
# redis_server = 'localhost'
r = redis.StrictRedis(host=redis_server, port=6379, db=0)

r.set('foo', 'bar')
print r.get('foo')