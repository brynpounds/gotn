import redis
from config.settings import REDIS_HOST, REDIS_PORT

r = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, decode_responses=True)

def update_score(email, mode, challenge_id, new_score):
    key = f"player:{email}:{mode}"
    current = r.hget(key, challenge_id)
    if current is None or int(new_score) > int(current):
        r.hset(key, challenge_id, new_score)

def get_scores(email, mode):
    key = f"player:{email}:{mode}"
    return r.hgetall(key)