import json
from hodor.utils.redistore import redis_store as rs

class Conversation:
    def __init__(self, uid=None, caller=None, status=None, store=rs, **kwargs):
        self.uid = str(uid)
        self.store = store
    
    @property
    def data(self):
        return self.store.hgetall(self.uid)
    
    @property
    def to_dict(self):
        keys = ['uid','caller','status']
        return { k:self.__dict__.get(k) for k in keys} 
    
    @property
    def to_json(self):
        return json.dumps(self.to_dict)
    
    def save(self):
        result = self.store.hmset(self.uid, self.to_dict)
    
    def set_param(self, key, value):
        resut = self.store.hset(self.uid, str(key),str(value))

    def get_param(self, key):
        return self.store.hget(self.uid,str(key))

    def del_param(self, key):
        return self.store.hdel(self.uid, key)
    
    @property
    def get_all(self):
        return self.store.hgetall(self.uid)


    @classmethod
    def from_uid(cls, uid, store=rs):
        data = store.hgetall(str(uid))
        new_dict = { k.decode(): v.decode() for k,v in data.items()}
        return cls.from_dict(new_dict)
    
    @classmethod
    def from_dict(cls, a_dict):
        return cls(**a_dict)

    def __str__(self):
        return str(self.to_dict)
        


