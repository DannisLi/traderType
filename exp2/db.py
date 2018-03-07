#-*- coding:utf8 -*-

import pymysql

def get_connection(db=None):
    conn = pymysql.connect(
        host = '219.224.169.45',
        user = 'lizimeng',
        password = 'codegeass',
        db = db,
        charset = 'utf8'
    )
    return conn
