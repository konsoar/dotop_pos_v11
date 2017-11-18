# -*- coding: utf-8 -*-
# Part of dotop. See LICENSE file for full copyright and licensing details.

""" Addons module.

This module serves to contain all dotop addons, across all configured addons
paths. For the code to manage those addons, see dotop.modules.

Addons are made available under `dotop.addons` after
dotop.tools.config.parse_config() is called (so that the addons paths are
known).

This module also conveniently reexports some symbols from dotop.modules.
Importing them from here is deprecated.

"""
__import__('pkg_resources').declare_namespace(__name__)
