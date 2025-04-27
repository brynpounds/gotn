import redis
from config.settings import REDIS_HOST, REDIS_PORT

r = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, decode_responses=True)

def setup_database(trouble_tickets):
    r.delete("trouble_tickets")
    for ticket in trouble_tickets:
        r.hset(f"ticket:{ticket['id']}", mapping=ticket)
        r.rpush("trouble_tickets", ticket['id'])

def get_all_tickets():
    ticket_ids = r.lrange("trouble_tickets", 0, -1)
    return [r.hgetall(f"ticket:{tid}") for tid in ticket_ids]

def get_ticket_by_id(ticket_id):
    return r.hgetall(f"ticket:{ticket_id}")