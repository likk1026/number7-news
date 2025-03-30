# -*- coding: utf-8 -*-
"""
Spyder Editor

This is a temporary script file.
"""

import mysql.connector

conn = mysql.connector.connect(
    host='127.0.0.1',
    user = 'root',
    password = '1234567890',
    database = 'allnews',
    buffered = True
    )


cursor = conn.cursor()  #建立一個資料庫操作物件
