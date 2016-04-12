#!/usr/bin/env python
#coding:utf-8

import sys
import urllib2
import urllib
import re
import sqlite3

url1 = 'http://cn163.net/2014the-tv-show/'
def inittable(url):
    '''初始化 tvinfo 表'''
    try:
        request = urllib2.Request(url)
        response = urllib2.urlopen(request)
    except urllib2.URLError,e:
        if hasattr(e,"code"):
            print e.code
        if hasattr(e,"reason"):
            print e.reason

    pattern = re.compile('<td><a href="(.*?)">(.*?)</a></td>')
    items = re.findall(pattern,response.read())
    con = sqlite3.connect("ttmj.db")
    con.text_factory = str
    cur = con.cursor()
    cur.execute("select count(*) from sqlite_master where type='table' and name ='tvinfo'")
    if cur.fetchone()[0] == 0 :
        cur.execute('''create table tvinfo
            (tvname varchar(255),tvurl varchar(255),tvposition varchar(255),tvnow varchar(255),active int)''')
    cur.execute("delete from tvinfo;")
    cur.executemany("insert into tvinfo (tvurl,tvname) values(?,?)",items)
    cur.execute("update tvinfo set active=1 where tvname like '破产姐妹第五季'")
    cur.execute("update tvinfo set active=1 where tvname like '极品老妈第三季'")
    cur.execute("update tvinfo set active=1 where tvname like '哥谭第二季'")
    cur.execute("update tvinfo set active=1 where tvname like '权力的游戏第六季'")
    con.commit()
    print 'tvinfo 装载数据完成'
    con.close()

def inittvposition():
    '''更新观看位置到最新'''
    con = sqlite3.connect("ttmj.db")
    con.text_factory = str
    cur = con.cursor()
    cur.execute("select * from tvinfo where active = 1")
    for row in cur.fetchall():
        #print row[0]
        try:
            request = urllib2.Request(row[1])
            response = urllib2.urlopen(request)
        except urllib2.URLError, e:
            if hasattr(e, "code"):
                print e.code
            if hasattr(e, "reason"):
                print e.reason
        pattern = re.compile('ed2k://.*?\.(S\d{2}E\d{2})\..*?/')
        items = re.findall(pattern, response.read())
        if len(items) == 0 :
            continue
        maxtv = max(items)
        #print row[0], maxtv
        cur.execute("update tvinfo set tvposition=? where tvname = ?", (maxtv, row[0]))
        con.commit()
    print 'tvinfo 初始化完成'
    con.close()

def updatenew():
    '''更新 tvinfo 的最新剧集列'''
    con = sqlite3.connect("ttmj.db")
    con.text_factory = str
    cur = con.cursor()
    cur.execute("select * from tvinfo where active = 1")
    for row in cur.fetchall():
        #print row
        try:
            request = urllib2.Request(row[1])
            response = urllib2.urlopen(request)
        except urllib2.URLError, e:
            if hasattr(e, "code"):
                print e.code
            if hasattr(e, "reason"):
                print e.reason
        pattern = re.compile('ed2k://.*?\.(S\d{2}E\d{2})\..*?/')
        items = re.findall(pattern, response.read())
        if len(items) == 0:
            continue
        maxtv = max(items)
        cur.execute("update tvinfo set tvnow=? where tvname = ?",(maxtv,row[0]))
        con.commit()
    con.close();

def geturl():
    '''抓出未观看的下载地址,并更新观看位置'''
    con = sqlite3.connect("ttmj.db")
    con.text_factory = str
    cur = con.cursor()
    cur.execute("select * from tvinfo where active = 1")
    for row in cur.fetchall():
        res = cmp(row[2], row[3])
        if res < 0:
            urllib.urlretrieve(row[1],'./ttmj.html')
            print row[0]
            print '最近观看到:' + row[2].split('E')[1] + '集'
            print '最新剧集为:' + row[3].split('E')[1] + '集'
            print "下载地址:\n"
            for i in range(int(row[2].split('E')[1]) + 1,int(row[3].split('E')[1]) + 1):
                seq = row[3].split('E')[0] + 'E' + str(i)
                fo = open('./ttmj.html')
                newpattern = re.compile('ed2k://.*?' + seq + '.*?/')
                newitem = re.findall(newpattern, fo.read())
                fo.close()
                print newitem[0]
                cur.execute("update tvinfo set tvposition=tvnow where active = 1")
                con.commit()
    con.close();

if __name__ == "__main__":
    if len(sys.argv) > 1 :
        if sys.argv[1] == 'init':
            inittable(url1)
            inittvposition()
    updatenew()
    geturl()
