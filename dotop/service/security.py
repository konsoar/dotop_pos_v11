# -*- coding: utf-8 -*-
# Part of dotop. See LICENSE file for full copyright and licensing details.

import dotop
import dotop.exceptions

def login(db, login, password):
    res_users = dotop.registry(db)['res.users']
    return res_users._login(db, login, password)

def check(db, uid, passwd):
    res_users = dotop.registry(db)['res.users']
    return res_users.check(db, uid, passwd)
