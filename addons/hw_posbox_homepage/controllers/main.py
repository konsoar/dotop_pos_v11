# -*- coding: utf-8 -*-

import logging
import os
import subprocess
import werkzeug

import dotop
from dotop import http

_logger = logging.getLogger(__name__)

index_style = """
        <style>
            body {
                width: 480px;
                margin: 60px auto;
                font-family: sans-serif;
                text-align: justify;
                color: #6B6B6B;
            }
            .text-red {
                color: #FF0000;
            }
        </style>
"""
index_template = """
<!DOCTYPE HTML>
<html>
    <head>
        <meta http-equiv="content-type" content="text/html; charset=utf-8">
        <title>智慧企业云-收银机</title>
""" + index_style + """
    </head>
    <body>
        <h1>收银机运行中</h1>
        <p>
        智慧企业云-收银机与智慧企业零售管理系统相结合，可以与小票打印机、扫描枪、钱箱、称重器等硬件设备连接使用。
        </p>
        <p>
        如果想要深入了解零售系统，可以联系智慧企业的客服人员。
        </p>
        <p>
        如果想要查看连接的硬件设备状态，可以点击这里：
        <a href='/hw_proxy/status'>查看硬件设备状态</a>.
        </p>
        <p>
        如果想要设置无线连接，请点击这里：<a href='/wifi'>无线网络设置</a>.
        </p>
        <p>
        如果想要开启远程调试访问，请点击这里：<a href='/remote_connect'>远程访问设置</a>.
        </p>
        %s
        <p>
        当前收银机的系统版本为<b>version 10</b>，
        此版本需要与智慧企业的版本相匹配。可以通过<a href='/hw_proxy/upgrade/'>系统更新</a>，来升级系统。
        </p>
    </body>
</html>
"""


class PosboxHomepage(dotop.addons.web.controllers.main.Home):

    def get_hw_screen_message(self):
        return """
<p>
    如果激活客显，需要重新安装收银机系统。必须确认系统的版本为V10上。
</p>
"""

    @http.route('/', type='http', auth='none', website=True)
    def index(self):
        #return request.render('hw_posbox_homepage.index',mimetype='text/html')
        return index_template % self.get_hw_screen_message()

    @http.route('/wifi', type='http', auth='none', website=True)
    def wifi(self):
        wifi_template = """
<!DOCTYPE HTML>
<html>
    <head>
    <meta http-equiv="content-type" content="text/html; charset=utf-8">
        <title>无线网络配置</title>
""" + index_style + """
    </head>
    <body>
        <h1>配置无线</h1>
        <p>
        在这里，可以配置收银机的无线网络连接。
        当前仅支持WAP开放网络。如果勾选【保存】选项，此连接将会被保存，下次收银机会首先尝试此连接。
        </p>
        <form action='/wifi_connect' method='POST'>
            <table>
                <tr>
                    <td>
                        ESSID:
                    </td>
                    <td>
                        <select name="essid">
"""
        try:
            f = open('/tmp/scanned_networks.txt', 'r')
            for line in f:
                line = line.rstrip()
                line = werkzeug.utils.escape(line)
                wifi_template += '<option value="' + line + '">' + line + '</option>\n'
            f.close()
        except IOError:
            _logger.warning("No /tmp/scanned_networks.txt")
        wifi_template += """
                        </select>
                    </td>
                </tr>
                <tr>
                    <td>
                        密码:
                    </td>
                    <td>
                        <input type="password" name="password" placeholder="optional"/>
                    </td>
                </tr>
                <tr>
                    <td>
                        保存:
                    </td>
                    <td>
                        <input type="checkbox" name="persistent"/>
                    </td>
                </tr>
                <tr>
                    <td/>
                    <td>
                        <input type="submit" value="开始连接"/>
                    </td>
                </tr>
            </table>
        </form>
        <p>
                点击下面按钮，可以清除已经保存的网络：
                <form action='/wifi_clear'>
                        <input type="submit" value="清除保存的网络连接"/>
                </form>
        </p>
        <form>
    </body>
</html>
"""
        return wifi_template

    @http.route('/wifi_connect', type='http', auth='none', cors='*',csrf=False)
    def connect_to_wifi(self, essid, password, persistent=False):
        if persistent:
                persistent = "1"
        else:
                persistent = ""

        subprocess.call(['/home/pi/dotop/addons/point_of_sale/tools/posbox/configuration/connect_to_wifi.sh', essid, password, persistent])
        return "开始连接 " + essid

    @http.route('/wifi_clear', type='http', auth='none', cors='*')
    def clear_wifi_configuration(self):
        os.system('/home/pi/dotop/addons/point_of_sale/tools/posbox/configuration/clear_wifi_configuration.sh')
        return "配置已经清除"

    @http.route('/remote_connect', type='http', auth='none', cors='*')
    def remote_connect(self):
        ngrok_template = """
<!DOCTYPE HTML>
<html>
    <head>
        <meta http-equiv="content-type" content="text/html; charset=utf-8">
        <title>Remote debugging</title>
        <script src="http://code.jquery.com/jquery-1.11.0.min.js"></script>
        <script>
           $(function () {
               var upgrading = false;
               $('#enable_debug').click(function () {
                   var auth_token = $('#auth_token').val();
                   if (auth_token == "") {
                       alert('Please provide an authentication token.');
                   } else {
                       $.ajax({
                           url: '/enable_ngrok',
                           data: {
                               'auth_token': auth_token
                           }
                       }).always(function (response) {
                           if (response === 'already running') {
                               alert('Remote debugging already activated.');
                           } else {
                               $('#auth_token').attr('disabled','disabled');
                               $('#enable_debug').html('Enabled remote debugging');
                               $('#enable_debug').removeAttr('href', '')
                               $('#enable_debug').off('click');
                           }
                       });
                   }
               });
           });
        </script>
""" + index_style + """
        <style>
            #enable_debug {
                padding: 10px;
                background: rgb(121, 197, 107);
                color: white;
                border-radius: 3px;
                text-align: center;
                margin: 30px;
                text-decoration: none;
                display: inline-block;
            }
            .centering{
                text-align: center;
            }
        </style>
    </head>
    <body>
        <h1>远程调试</h1>
        <p class='text-red'>
        可以允许远程访问收银机，以及整个局域网。仅将此功能开放给信任的人员。
        </p>
        <div class='centering'>
            <input type="text" id="auth_token" size="42" placeholder="Authentication Token"/> <br/>
            <a id="enable_debug" href="#">开启远程调试</a>
        </div>
    </body>
</html>
"""
        return ngrok_template

    @http.route('/enable_ngrok', type='http', auth='none', cors='*')
    def enable_ngrok(self, auth_token):
        if subprocess.call(['pgrep', 'ngrok']) == 1:
            subprocess.Popen(['ngrok', 'tcp', '-authtoken', auth_token, '-log', '/tmp/ngrok.log', '22'])
            return 'starting with ' + auth_token
        else:
            return 'already running'