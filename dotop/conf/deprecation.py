# -*- coding: utf-8 -*-
# Part of dotop. See LICENSE file for full copyright and licensing details.

""" Regroup variables for deprecated features.

To keep the dotop server backward compatible with older modules, some
additional code is needed throughout the core library. This module keeps
track of those specific measures by providing variables that can be unset
by the user to check if her code is future proof.

In a perfect world, all these variables are set to False, the corresponding
code removed, and thus these variables made unnecessary.
"""

# If True, the Python modules inside the dotop namespace are made available
# without the 'dotop.' prefix. E.g. dotop.osv.osv and osv.osv refer to the
# same module.
# Introduced around 2011.02.
# Change to False around 2013.02.
open_dotop_namespace = False

# If True, dotop.netsvc.LocalService() can be used to lookup reports or to
# access dotop.workflow.
# Introduced around 2013.03.
# Among the related code:
# - The dotop.netsvc.LocalService() function.
# - The dotop.report.interface.report_int._reports dictionary.
# - The register attribute in dotop.report.interface.report_int (and in its
# - auto column in ir.actions.report.xml.
# inheriting classes).
allow_local_service = True

# Applies for the register attribute in dotop.report.interface.report_int.
# See comments for allow_local_service above.
# Introduced around 2013.03.
allow_report_int_registration = True
