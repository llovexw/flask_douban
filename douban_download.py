# -*- coding = utf-8 -*-
# @Time:2021/03/24 15:42
# @Author:Luorui
# @File:douban_download.py
# @Software:PyCharm

from bs4 import BeautifulSoup  # 网页解析，获取数据
import re
import urllib.request
import xlwt  # 进行excel操作
import sqlite3  # 进行SQLite
import os

findLink = r'<a href="(.*?)".*>'
findImg = r'<img.*src="(.*?)".*>'
findTitle = r'<span class="title">(.*?)</span>'
findRating = r'<span class="rating_num" property="v:average">(.*?)</span>'
findJudge = r'<span>(\d*?)人评价</span>'
findInq = r'<span class="inq">(.*?)</span>'
findBd = re.compile('<p class="">(.*?)</p>', re.S)      #re.S匹配空格


def main():
    baseurl = "https://movie.douban.com/top250?start="
    # 爬取网页
    datalist = getData(baseurl)
    #savePath = "豆瓣电影Top250.xls"
    #saveData(datalist, savePath)
    dbpath = "movie.db"
    if os.path.exists(dbpath):
        os.remove(dbpath)
        print("该数据库已存在，将先删除原有数据库...")
    saveData2DB(datalist,dbpath)

def getvideourl(name):
    pass

def getData(baseurl):
    datalist = []
    for i in range(0, 10):
        url = baseurl + str(i * 25)
        html = askURL(url)

        soup = BeautifulSoup(html, "html.parser")   #解析网页
        for item in soup.find_all('div', class_=('item')):
            # print(item)    #测试：查看电影的item全部信息
            item = str(item)
            data = []

            link = re.findall(findLink, item)[0]    # 添加链接
            data.append(link)

            img = re.findall(findImg, item)[0]      # 添加图片
            data.append(img)

            titles = re.findall(findTitle, item)
            if len(titles) == 2:
                ctitle = titles[0]
                data.append(ctitle)                 #添加中文名
                otitle = titles[1].replace("/", "")
                data.append(otitle.strip())         #添加外文名
            else:
                ctitle = titles[0]
                data.append(titles[0])
                data.append(' ')  # 外文名留空

            rating = re.findall(findRating, item)[0]
            data.append(rating)  # 添加评分

            judgeNum = re.findall(findJudge, item)[0]
            data.append(judgeNum)  # 评价人数

            inq = re.findall(findInq, item)
            if len(inq) != 0:
                inq = inq[0].replace("。", "")  # 去掉句号
                data.append(inq)  # 添加概述
            else:
                data.append(" ")

            bd = re.findall(findBd, item)[0]
            bd = re.sub('<br/>', ' ', bd)  # 必须要是字符串才能被删减、替换
            bd = re.sub('/', ' ', bd)
            bd = re.sub('\xa0',' ',bd)  #\xa0属于latin1(ISO/IEC_8859-1)中的扩展字符集字符,代表空白符&nbsp(non-breaking space)。
            bd = re.sub('\n',' ',bd)    #去除换行
            data.append(bd.strip())     #添加背景

            videourl = 'https://so.iqiyi.com/so/q_' + urllib.parse.quote(ctitle)  # 保存电影链接地址

            data.append(videourl)

            datalist.append(data)

    return datalist


def askURL(url):
    head = 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.108 Safari/537.36'
    req = urllib.request.Request(url)
    req.add_header('User-Agent', head)

    response = urllib.request.urlopen(req)
    html = response.read().decode('utf-8')

    print(url)
    return html


def saveData(datalist, savepath):
    book = xlwt.Workbook(encoding="utf-8", style_compression=0)
    sheet = book.add_sheet('豆瓣电影Top250', cell_overwrite_ok=True)
    col = ("电影详情链接", "图片链接", "影片中文名", "影片外文名", "评分", "评价数", "概述", "相关性息","电影观看链接")
    for i in range(0, 9):
        sheet.write(0, i, col[i])
    for i in range(0, 250):
        print("第%d条" % i)
        data = datalist[i]
        for j in range(0, 9):
            sheet.write(i + 1, j, data[j])

    book.save(savepath)
    print("存储完成")

def saveData2DB(datalist,dbpath):
    init_db(dbpath)
    conn = sqlite3.connect(dbpath)
    cursor = conn.cursor()
    sql = '''insert into movieTop250(
                info_link,pic_link,cname,ename,score,rated,introduction,info,video_link)
                values(?,?,?,?,?,?,?,?,?)
    '''
    cursor.executemany(sql,datalist)    #批量执行语句，在sqlite3中用?代替
    conn.commit()
    conn.close()

#初始化数据库
def init_db(dbpath):
    sql = '''
        create table movieTop250
        (
        id integer primary key autoincrement,
        info_link text,
        pic_link text,
        cname varchar,
        ename varchar,
        score numeric,
        rated numeric,
        introduction text,
        info text,
        video_link text)
    '''
    conn = sqlite3.connect(dbpath)
    cursor = conn.cursor()
    cursor.execute(sql)
    conn.commit()
    conn.close()


if __name__ == "__main__":
    main()
    print("爬取完毕")
