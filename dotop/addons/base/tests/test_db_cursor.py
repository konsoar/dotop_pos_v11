# -*- coding: utf-8 -*-
# Part of dotop. See LICENSE file for full copyright and licensing details.

import unittest

import dotop
from dotop.tests import common
from dotop.tools.misc import mute_logger

ADMIN_USER_ID = common.ADMIN_USER_ID

def registry():
    return dotop.registry(common.get_db_name())


class TestExecute(unittest.TestCase):
    """ Try cr.execute with wrong parameters """

    @mute_logger('dotop.sql_db')
    def test_execute_bad_params(self):
        """
        Try to use iterable but non-list or int params in query parameters.
        """
        with registry().cursor() as cr:
            with self.assertRaises(ValueError):
                cr.execute("SELECT id FROM res_users WHERE login=%s", 'admin')
            with self.assertRaises(ValueError):
                cr.execute("SELECT id FROM res_users WHERE id=%s", 1)
            with self.assertRaises(ValueError):
                cr.execute("SELECT id FROM res_users WHERE id=%s", '1')
