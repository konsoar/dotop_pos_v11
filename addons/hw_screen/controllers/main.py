# -*- coding: utf-8 -*-

from dotop import http
from dotop.tools import config
from dotop.addons.web.controllers import main as web
from dotop.addons.hw_posbox_homepage.controllers import main as homepage

import logging
import netifaces as ni
import os
from subprocess import call
import time
import threading

self_port = str(config['xmlrpc_port'] or 8069)

_logger = logging.getLogger(__name__)

class Homepage(homepage.PosboxHomepage):

    def get_hw_screen_message(self):
        return """
<p>
如果需要在其他设备中显示当前收银机信息，<a href='/point_of_sale/display'>可以点击这里</a>。
</p>
"""

class HardwareScreen(web.Home):

    event_data = threading.Event()
    pos_client_data = {'rendered_html': False,
                       'ip_from': False}
    display_in_use = ''
    failure_count = {}

    def _call_xdotools(self, keystroke):
        os.environ['DISPLAY'] = ":0.0"
        os.environ['XAUTHORITY'] = "/run/lightdm/pi/xauthority"
        try:
            call(['xdotool', 'key', keystroke])
            return "xdotool succeeded in stroking " + keystroke
        except:
            return "xdotool threw an error, maybe it is not installed on the posbox"

    @http.route('/hw_proxy/display_refresh', type='json', auth='none', cors='*')
    def display_refresh(self):
        return self._call_xdotools('F5')

    # POS CASHIER'S ROUTES
    @http.route('/hw_proxy/customer_facing_display', type='json', auth='none', cors='*')
    def update_user_facing_display(self, html=None):
        request_ip = http.request.httprequest.remote_addr
        if request_ip == HardwareScreen.pos_client_data.get('ip_from', ''):
            HardwareScreen.pos_client_data['rendered_html'] = html
            HardwareScreen.event_data.set()

            return {'status': 'updated'}
        else:
            return {'status': 'failed'}

    @http.route('/hw_proxy/take_control', type='json', auth='none', cors='*')
    def take_control(self, html=None):
        # ALLOW A CASHIER TO TAKE CONTROL OVER THE POSBOX, IN CASE OF MULTIPLE CASHIER PER POSBOX
        HardwareScreen.pos_client_data['rendered_html'] = html
        HardwareScreen.pos_client_data['ip_from'] = http.request.httprequest.remote_addr
        HardwareScreen.event_data.set()

        return {'status': 'success',
                'message': 'You now have access to the display'}

    @http.route('/hw_proxy/test_ownership', type='json', auth='none', cors='*')
    def test_ownership(self):
        if HardwareScreen.pos_client_data.get('ip_from') == http.request.httprequest.remote_addr:
            return {'status': 'OWNER'}
        else:
            return {'status': 'NOWNER'}

    # POSBOX ROUTES (SELF)
    @http.route('/point_of_sale/display', type='http', auth='none')
    def render_main_display(self):
        return self._get_html()

    @http.route('/point_of_sale/get_serialized_order', type='json', auth='none')
    def get_serialized_order(self):
        request_addr = http.request.httprequest.remote_addr
        result = HardwareScreen.pos_client_data
        if HardwareScreen.display_in_use and request_addr != HardwareScreen.display_in_use:
            if not HardwareScreen.failure_count.get(request_addr):
                HardwareScreen.failure_count[request_addr] = 0
            if HardwareScreen.failure_count[request_addr] > 0:
                time.sleep(10)
            HardwareScreen.failure_count[request_addr] += 1
            return {'rendered_html': """<div class="pos-customer_facing_display"><p>没有授权。另一个浏览器在使用客户端显示，请刷新。</p></div> """,
                    'stop_longpolling': True,
                    'ip_from': request_addr}

        # IMPLEMENTATION OF LONGPOLLING
        # Times out 2 seconds before the JS request does
        if HardwareScreen.event_data.wait(28):
            HardwareScreen.event_data.clear()
            HardwareScreen.failure_count[request_addr] = 0
            return result
#         return {'rendered_html': False,
#                 'ip_from': HardwareScreen.pos_client_data['ip_from']}
        return result

    def _get_html(self):
        cust_js = None
        interfaces = ni.interfaces()
        my_ip = '127.0.0.1'
        HardwareScreen.display_in_use = http.request.httprequest.remote_addr

        with open(os.path.join(os.path.dirname(__file__), "../static/src/js/worker.js")) as js:
            cust_js = js.read()

        with open(os.path.join(os.path.dirname(__file__), "../static/src/css/cust_css.css")) as css:
            cust_css = css.read()

        display_ifaces = ""
        for iface_id in interfaces:
            iface_obj = ni.ifaddresses(iface_id)
            ifconfigs = iface_obj.get(ni.AF_INET, [])
            for conf in ifconfigs:
                if conf.get('addr'):
                    display_ifaces += "<tr><td>" + iface_id + "</td>"
                    display_ifaces += "<td>" + conf.get('addr') + "</td>"
                    display_ifaces += "<td>" + conf.get('netmask') + "</td></tr>"
                    # What is my external IP ?
                    if iface_id != 'lo':
                        my_ip = conf.get('addr')

        my_ip_port = my_ip + ":" + self_port

        html = """
            <!DOCTYPE html>
            <html>
                <head>
                <meta http-equiv="content-type" content="text/html; charset=utf-8">
                <title class="origin">智慧企业-收银机</title>
                <script type="text/javascript" class="origin" src="../web/static/lib/jquery/jquery.js" >
                </script>
                <script type="text/javascript" class="origin">
                    """ + cust_js + """
                </script>
                <link rel="stylesheet" class="origin" href="../web/static/lib/bootstrap/css/bootstrap.css" >
                </link>
                <script class="origin" src="../web/static/lib/bootstrap/js/bootstrap.min.js"></script>
                <style class="origin">
                    """ + cust_css + """
                </style>
                </head>
                <body class="original_body">
                    <div hidden class="shadow"></div>
                    <div class="container">
                    <div class="row">
                        <div class="col-md-4 col-md-offset-4">
                            <h1>智慧企业-收银机</h1>
                            <h2>收银机信息</h2>
                            <h3>IP地址</h3>
                                <table id="table_ip" class="table table-condensed">
                                    <tr>
                                        <th>网卡</th>
                                        <th>IP</th>
                                        <th>子网掩码</th>
                                    </tr>
                                    """ + display_ifaces + """
                                </table>
                            <p>一旦开始零售会话，客户购物车内容将在这里显示。</p>
                            <p>智慧企业V11 或者更高版本。</p>
                        </div>
                    </div>
                    </div>
                </body>
                </html>
            """
        return html
