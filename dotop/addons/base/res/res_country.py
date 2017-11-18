# -*- coding: utf-8 -*-
# Part of dotop. See LICENSE file for full copyright and licensing details.

import re
import logging
from dotop import api, fields, models
from psycopg2 import IntegrityError
from dotop.tools.translate import _
_logger = logging.getLogger(__name__)


@api.model
def location_name_search(self, name='', args=None, operator='ilike', limit=100):
    if args is None:
        args = []

    records = self.browse()
    if len(name) == 2:
        records = self.search([('code', 'ilike', name)] + args, limit=limit)

    search_domain = [('name', operator, name)]
    if records:
        search_domain.append(('id', 'not in', records.ids))
    records += self.search(search_domain + args, limit=limit)

    # the field 'display_name' calls name_get() to get its value
    return [(record.id, record.display_name) for record in records]


class Country(models.Model):
    _name = 'res.country'
    _description = 'Country'
    _order = 'name'

    name = fields.Char(string='Country Name', required=True, translate=True, help='The full name of the country.')
    code = fields.Char(string='Country Code', size=2,
                help='The ISO country code in two chars. \nYou can use this field for quick search.')
    address_format = fields.Text(help="""You can state here the usual format to use for the \
addresses belonging to this country.\n\nYou can use the python-style string patern with all the field of the address \
(for example, use '%(street)s' to display the field 'street') plus
            \n%(state_name)s: the name of the state
            \n%(state_code)s: the code of the state
            \n%(country_name)s: the name of the country
            \n%(country_code)s: the code of the country""",
            default='%(street)s\n%(street2)s\n%(city)s %(state_code)s %(zip)s\n%(country_name)s')
    currency_id = fields.Many2one('res.currency', string='Currency')
    image = fields.Binary(attachment=True)
    phone_code = fields.Integer(string='Country Calling Code')
    country_group_ids = fields.Many2many('res.country.group', 'res_country_res_country_group_rel',
                         'res_country_id', 'res_country_group_id', string='Country Groups')
    state_ids = fields.One2many('res.country.state', 'country_id', string='States')

    _sql_constraints = [
        ('name_uniq', 'unique (name)',
            'The name of the country must be unique !'),
        ('code_uniq', 'unique (code)',
            'The code of the country must be unique !')
    ]

    name_search = location_name_search

    @api.model
    def create(self, vals):
        if vals.get('code'):
            vals['code'] = vals['code'].upper()
        return super(Country, self).create(vals)

    @api.multi
    def write(self, vals):
        if vals.get('code'):
            vals['code'] = vals['code'].upper()
        return super(Country, self).write(vals)

    @api.multi
    def get_address_fields(self):
        self.ensure_one()
        return re.findall(r'\((.+?)\)', self.address_format)

    def get_country_china(self):
        country_ids = self.search(['|',('name','=',u'中国'),('code','=','CN')])
        return country_ids and country_ids[0].id or False


class CountryGroup(models.Model):
    _description = "Country Group"
    _name = 'res.country.group'

    name = fields.Char(required=True)
    country_ids = fields.Many2many('res.country', 'res_country_res_country_group_rel',
                                   'res_country_group_id', 'res_country_id', string='Countries')


class CountryState(models.Model):
    _description = "Country state"
    _name = 'res.country.state'
    _order = 'code'

    country_id = fields.Many2one('res.country', string='Country', required=True,ondelete='cascade')
    name = fields.Char(string='State Name', required=True,
               help='Administrative divisions of a country. E.g. Fed. State, Departement, Canton')
    code = fields.Char(string='State Code', help='The state code.')

    name_search = location_name_search

    # _sql_constraints = [
    #     ('name_code_uniq', 'unique(country_id, code)', 'The code of the state must be unique by country !')
    # ]

class ResCity(models.Model):
    _name = "res.city"
    _description = u"城市"
    
    name = fields.Char(u'名称', size=100,required=True, help=u"城市名称")
    simple_name = fields.Char(u'简称', size=20,help=u"城市简称")
    code = fields.Char(u'行政区号', size=10)
    province_id = fields.Many2one('res.country.state', u'省份', required=True,ondelete='cascade')
        
    # _sql_constraints = [
    #     ('code', 'unique(code)', u'城市行政区号已存在!'),
    # ]

class ResCounty(models.Model):
    _name = "res.county"
    _description = u"区/县"
    
    name = fields.Char(u'名称', size=20, required=True, help=u"区/县名称")
    code = fields.Char(u'行政区号', size=10, help=u"区/县行政区号")
    city_id = fields.Many2one('res.city', u'城市', required=True,ondelete='cascade')
    
    
    