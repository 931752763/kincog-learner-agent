# -*- coding: utf-8 -*-
from typing import Dict, List

# 简单内存版memory，后续可接入数据库/redis
_user_memory_store: Dict[str, List[dict]] = {}

def get_user_memory(user_id: str) -> List[dict]:
    return _user_memory_store.get(user_id, [])

def append_user_memory(user_id: str, record: dict):
    if user_id not in _user_memory_store:
        _user_memory_store[user_id] = []
    _user_memory_store[user_id].append(record) 