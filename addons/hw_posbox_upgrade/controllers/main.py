# -*- coding: utf-8 -*-
# Part of dotop. See LICENSE file for full copyright and licensing details.

import logging
import os
import subprocess
import threading

from dotop import http

import dotop.addons.hw_proxy.controllers.main as hw_proxy

_logger = logging.getLogger(__name__)

upgrade_template = """
<!DOCTYPE HTML>
<html>
    <head>
        <meta http-equiv="content-type" content="text/html; charset=utf-8">
        <title>智慧企业-收银机系统更新</title>
        <script src="http://code.jquery.com/jquery-1.11.0.min.js"></script>
        <script>
        $(function(){
            var upgrading = false;
            $('#upgrade').click(function(){
                console.log('click');
                if(!upgrading){
                    upgrading = true;
                    $('#upgrade').text('Upgrading, Please Wait');
                    $.ajax({
                        url:'/hw_proxy/perform_upgrade/'
                    }).then(function(status){
                        $('#upgrade').html('Upgrade successful, restarting the posbox...');
                        $('#upgrade').off('click');
                    },function(){
                        $('#upgrade').text('Upgrade Failed');
                    });
                }
            });
        });
        </script>
        <style>
        body {
            width: 480px;
            margin: 60px auto;
            font-family: sans-serif;
            text-align: justify;
            color: #6B6B6B;
        }
        .centering{
            text-align: center;
        }
        #upgrade {
            padding: 20px;
            background: rgb(121, 197, 107);
            color: white;
            border-radius: 3px;
            text-align: center;
            margin: 30px; 
            text-decoration: none;
            display: inline-block;
        }
        </style>
    </head>
    <body>
        <h1>收银机系统更新</h1>
        <p> 通过网络来更新升级智慧企业-收银机系统。<p>
        <p>
        点击【升级】按钮，可以升级收银机系统。更新预计会花费几分钟， 在此期间<b>请不要重启收银机或者断电</b> 
        </p>
        <p>
        最新补丁包:
        </p>
        <pre>
"""
upgrade_template += subprocess.check_output("git --work-tree=/home/pi/dotop/ --git-dir=/home/pi/dotop/.git log -1", shell=True).replace("\n", "<br/>")
upgrade_template += """
        </pre>
        <div class='centering'>
            <a href='#' id='upgrade'>升级</a>
        </div>
    </body>
</html>

"""

class PosboxUpgrader(hw_proxy.Proxy):
    def __init__(self):
        super(PosboxUpgrader,self).__init__()
        self.upgrading = threading.Lock()

    @http.route('/hw_proxy/upgrade', type='http', auth='none', )
    def upgrade(self):
        return upgrade_template 
    
    @http.route('/hw_proxy/perform_upgrade', type='http', auth='none')
    def perform_upgrade(self):
        self.upgrading.acquire()

        os.system('/home/pi/dotop/addons/point_of_sale/tools/posbox/configuration/posbox_update.sh')
        
        self.upgrading.release()
        return 'SUCCESS'
