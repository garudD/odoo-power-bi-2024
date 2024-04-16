"""Part of odoo. See LICENSE file for full copyright and licensing details."""
import re
import ast
import json
import functools
import logging
from odoo.exceptions import AccessError
from datetime import datetime
from odoo import http
from odoo.addons.api_restful_odoo.common import (
    extract_arguments,
    invalid_response,
    valid_response,
)
from odoo.http import request

_logger = logging.getLogger(__name__)


def validate_token(func):
    """."""

    @functools.wraps(func)
    def wrap(self, *args, **kwargs):
        """."""
        access_token = request.httprequest.headers.get("token")
        if not access_token:
            return invalid_response("access_token_not_found", "missing access token in request header", 401)
        access_token_data = (
            request.env["api.access_token"].sudo().search([("token", "=", access_token)], order="id DESC", limit=1)
        )

        if access_token_data.find_one_or_create_token(user_id=access_token_data.user_id.id) != access_token:
            return invalid_response("access_token", "token seems to have expired or invalid", 401)

        request.session.uid = access_token_data.user_id.id
        request.uid = access_token_data.user_id.id
        return func(self, *args, **kwargs)

    return wrap


# _routes = ["/api/<model>", "/api/<model>/<id>", "/api/<model>/<id>/<action>","/api/raw/<model>/<method>"]
_routes = ["/api/raw/<model>/<method>"]
General_Methods = ['get_sliders','get_news','get_faq','get_products','get_pos','get_stations','get_lines','get_claim_types','get_claim_categories','set_claim','set_client','order_card']

class APIController(http.Controller):
    """."""

    def __init__(self):
        self._model = "ir.model"


    @validate_token
    @http.route(_routes, type="http", auth="none", methods=["GET"], csrf=False,cors='*')
    def get(self, model=None, method=None, id=None, **payload):
        """
        """
        try:
            ioc_name = model
            model = request.env[self._model].search([("model", "=", model)], limit=1)
            if model:
                domain, fields, offset, limit, order = extract_arguments(payload)
                data = request.env[model.model].search_read(
                    domain=domain, fields=fields, offset=offset, limit=limit, order=order,
                )
                if method and method not in General_Methods:
                    return invalid_response("Invaild Method Found",message='%s Method not Found in API' % method,)
                if model and method:
                    if method == 'get_sliders':
                        records = request.env[model.model].sudo().search([('media_type','=','slider'),('state','=','active')])
                        data = []
                        for record in records:
                            data.append({'title':record.title,'description': record.description,'image_res': record.image_res})

                    if method == 'get_news':
                        records = request.env[model.model].sudo().search([('media_type','=','news'),('state','=','active')])
                        data = []
                        for record in records:
                            data.append({'title':record.title,'description': record.description,'image_res': record.image_res})

                    if method == 'get_faq':
                        records = request.env[model.model].sudo().search([('media_type','=','faq'),('state','=','active')])
                        data = []
                        for record in records:
                            data.append({'title':record.title,'description': record.description})

                    if method == 'get_products':
                        records = request.env[model.model].sudo().search([])
                        data = []
                        for record in records:
                            data.append({'id':record.id,'description': record.description,'name':record.name,'image_1920': record.image_1920})

                    if method == 'get_pos':
                        records = request.env[model.model].sudo().search([('partner_type','=','pos'),('state','=','active')])
                        data = []
                        for record in records:
                            data.append({'id':record.id,
                                        'code': record.code,
                                        'name':record.name,
                                        'street': record.street,
                                        'city':record.city,
                                        'phone':record.phone,
                                        'partner_latitude':record.partner_latitude,
                                        'partner_longitude': record.partner_longitude})

                    if method == 'get_stations':
                        records = request.env[model.model].sudo().search([('partner_type','=','station'),('state','=','active')])
                        data = []
                        for record in records:
                            data.append({'id':record.id,
                                        'code': record.code,
                                        'name':record.name,
                                        'partner_latitude':record.partner_latitude,
                                        'partner_longitude': record.partner_longitude})

                    if method == 'get_lines':
                        records = request.env[model.model].sudo().search([('partner_type','=','line'),('state','=','active')])
                        data = []
                        for record in records:
                            station_list = []
                            for station_rec in record.station_ids:
                                station_list.append({'order':station_rec.sequence_ref,
                                                    'station_id':station_rec.station_id.id,
                                                    'terminus': station_rec.terminus,
                                                    'correspondence_ids': station_rec.correspondence_ids.ids})
                            departure_list = []
                            for departure in record.departure_ids:
                                departure_list.append({'period':departure.period.id,
                                                    'timetable':departure.timetable.id,
                                                    'station_id': departure.station_id.id,
                                                    'first_departure': departure.first_departure,
                                                    'last_departure':departure.last_departure})
                            data.append({'id':record.id,
                                        'code': record.code,
                                        'name':record.name,
                                        'rate':record.rate,
                                        'frequency': record.frequency,
                                        'mileage': record.mileage,
                                        'travel_time': record.travel_time,
                                        'nbr_buses': record.number_of_buses,
                                        'station_ids': station_list,
                                        'departure_ids': departure_list
                                        })

                    if method == 'get_claim_types':
                        records = request.env[model.model].sudo().search([('active','=',True)])
                        data = []
                        for record in records:
                            data.append({'name':record.name})

                    if method == 'get_claim_categories':
                        records = request.env[model.model].sudo().search([])
                        data = []
                        for record in records:
                            data.append({'name':record.name,'claim_type': record.claim_type})
                            
                    if data:
                        return valid_response(data)
                    else:
                        return valid_response(data)
            return invalid_response(
                "invalid object model", "The model %s is not available in the registry." % ioc_name,
            )
        except AccessError as e:
            return invalid_response("Access error", "Error: %s" % e.name)

    @validate_token
    @http.route(_routes, type="http", auth="none", methods=["POST"], csrf=False,cors='*')
    def post(self, model=None, method=None, id=None, **payload):
        """Create a new record.
        Basic sage:
        import requests

        headers = {
            'content-type': 'application/x-www-form-urlencoded',
            'charset': 'utf-8',
            'token': 'token'
        }
        sale_order = requests.post(url="%s/api/sale.order/" %"http://localhost:8069", data=payload, headers=headers)
        print(sale_order)
        print(sale_order.text)

        order_id = json.loads(sale_order.text).get("data")[0].get('id')
        print(order_id)

        payload = {
            'price_unit': 4000,
            'product_id': 1,
            'order_id': order_id
        }

        order_line1 = requests.post(url="%s/api/sale.order.line/" %"http://localhost:8069", data=payload, headers=headers)
        print(order_line1)
        print(order_line1.text)


        payload = {
            'price_unit': 5000,
            'product_id': 2,
            'order_id': order_id

        }

        order_line2 = requests.post(url="%s/api/sale.order.line/" %"http://localhost:8069", data=payload, headers=headers)
        print(order_line2)
        print(order_line2.text)
        """
        ioc_name = model
        model = request.env[self._model].search([("model", "=", model)], limit=1)
        if method and method not in General_Methods:
            return invalid_response("Invaild Method Found",message='%s Method not Found in API' % method,)
        if model and method:
            try:
                if method == 'set_client':
                    data = []
                    if not payload.get('code'):
                        return invalid_response("Error",message='partner code is required')
                    records = request.env[model.model].sudo().search([('partner_type','=','client'),('code','=', payload.get('code'))])
                    if not records:
                        payload.update({'partner_type':'client'})
                        records = request.env[model.model].sudo().create(payload)
                    if records:
                        records.sudo().write(payload)
                    data.append({'partner_id': records.id})

                if method == 'order_card':
                    data = []
                    if not payload.get('client_code'):
                        return invalid_response("Error",message='client code is required')
                    if not payload.get('product_id'):
                        return invalid_response("Error",message='product is required')
                    records = request.env['res.partner'].sudo().search([('partner_type','=','client'),('code','=', payload.get('client_code'))])
                    # if not records:
                    #     records = request.env[model.model].sudo().create(payload)
                    if records:
                        records = request.env[model.model].sudo().create(
                            {
                                'partner_id': records.id,
                                'date_order': datetime.today().strftime('%Y-%m-%d'),
                                'order_line': [(0,0,{'product_id': int(payload.get('product_id'))})]
                            }
                        )
                        data.append({'order_id': records.id})

                if method == 'set_claim':
                    data = []
                    if not payload.get('client_code'):
                        return invalid_response("Error",message='client code is required')
                    if not payload.get('name'):
                        return invalid_response("Error",message='subject is required')
                    records = request.env['res.partner'].sudo().search([('partner_type','=','client'),('code','=', payload.get('client_code'))])
                    # if not records:
                    #     records = request.env[model.model].sudo().create(payload)
                    if records:
                        records = request.env[model.model].sudo().create({
                            'date':payload.get('date'),
                            'num_bus':payload.get('num_bus'),
                            'code':payload.get('client_code'),
                            'name':payload.get('name'),
                            'line_id':payload.get('line_id'),
                            'description':payload.get('description'),
                            'is_called_back':payload.get('is_called_back'),
                            'claim_type':payload.get('claim_type'),
                            'categ_id':payload.get('claim_category'),
                        })
                        data.append({'order_id': records.id})
                return valid_response(data)
            except Exception as e:
                request.env.cr.rollback()
                return invalid_response("params", e)
        return invalid_response("invalid object model", "The model %s is not available in the registry." % ioc_name,)
