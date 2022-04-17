# coding = utf8
'''
@Description:
@Author: Chenhao Xing
@Email: axchtzon@gmail.com
@Date: 2020-05-23 10:49:40
@LastEditTime: 2020-05-28 15:02:24
@LastEditors: Chenhao Xing
'''

from bs4 import BeautifulSoup  # 网页解析·获取数据
import re  # 正则表达式·进行文字匹配
import urllib.request
import urllib.error  # 指定URL·获取网页数据
# import xlwt  # 进行excel操作
# import sqlite3  # 进行SQLLite数据库操作
# import xlwt
import pymysql


def main():
    baseurl = "https://movie.douban.com/top250?start="
    # 爬取网页
    askUrl(baseurl)
    datalist = getData(baseurl)
    # 保存数据到数据库
    saveDataDb(datalist)

    # 保存数据到excel
    savepath = "./豆瓣电影Top250.xls"
    saveData(savepath, datalist)


# 影片名字
findName = re.compile(r'<span class="title">(.*?)</span>')
# 影片链接
findLink = re.compile(r'<a href="(.*?)">')
# 影片图片链接
findImgSrc = re.compile(r'<img alt=.*src="(.*?)"', re.S)
# 影片演职员表
findBd = re.compile(r'<p class="">(.*?)</p>', re.S)
# 影片简介
findTran = re.compile(r'<span class="inq">(.*?)</span>')
# 影片评分
findMarkNum = re.compile(r'<span class="rating_num".*">(.*?)</span>')
# 影片评价人数
findMarkPeople = re.compile(r'<span>(\d*)人评价</span>')


# datalist = []

# 访问网页
def askUrl(url):
    head = {
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.61 Safari/537.36 Edg/83.0.478.37"
    }
    html = ""
    req = urllib.request.Request(url=url, headers=head)
    response = urllib.request.urlopen(req)
    html = response.read().decode("utf-8")

    return html


# 爬取网页
def getData(baseurl):
    datalist = []
    for i in range(0, 10):
        url = baseurl + str(i * 25)
        html = askUrl(url)
        # 2.逐一解析数据
        soup = BeautifulSoup(html, "html.parser")
        for item in soup.find_all('div', class_="item"):
            # print(item)
            data = []
            item = str(item)
            # 电影名
            name = re.findall(findName, item)[0]
            data.append(name)
            # 详情链接
            link = re.findall(findLink, item)[0]
            data.append(link)
            # 图片链接
            imgSrc = re.findall(findImgSrc, item)[0]
            data.append(imgSrc)
            # 演职员
            bd = re.findall(findBd, item)[0]
            bd = bd.replace(" ", "")
            bd = bd.replace("<br/>", " ")
            bd = bd.replace("\n", " ")
            data.append(bd)
            # 简介
            try:
                tran = re.findall(findTran, item)[0]
                if len(tran) != 0:
                    tran = tran.replace("。", "")
                    data.append(tran)
            except Exception as result:
                data.append("无")
                pass
            # 评分
            markNum = re.findall(findMarkNum, item)[0]
            data.append(markNum)
            # 评价人数
            markPeople = re.findall(findMarkPeople, item)[0]
            data.append(markPeople)
            # 保存到列表
            datalist.append(data)

    return datalist


# 保存数据到excel
def saveData(savepath, datalist):
    workbook = xlwt.Workbook(encoding="utf-8")
    worksheet = workbook.add_sheet('排名', cell_overwrite_ok=True)
    # 添加列表名
    col = ('排名', '影片名字', '电影详情链接', '图片链接', '演职员', '简介', '评分', '评价人数')
    for i in range(0, 8):
        worksheet.write(0, i, col[i])
    # 存数据到excel表
    for i in range(0, len(datalist)):
        for j in range(0, 7):
            worksheet.write(i + 1, 0, 'TOP%s' % (i + 1))
            try:
                worksheet.write(i + 1, j + 1, datalist[i][j])
            except Exception as result:
                pass
    if workbook.save(savepath):
        print('yes')


# 保存数据到数据库
def saveDataDb(datalist):
    init__db()

    conn = pymysql.connect(
        host='localhost',
        user='root',
        password='5586305',
        db='pydb_movie250',
        charset='utf8'
    )
    cur = conn.cursor()

    for data in datalist:
        for index in range(len(data)):
            # for i in range(len(data)):
            data[index] = '"' + data[index] + '"'

        insert_sqli = 'insert into top25012(cname,info_link,pic_link,bd,tran,score,rated) values(%s)' % ",".join(data)
        cur.execute(insert_sqli)
    conn.commit()
    conn.close()


# 连接数据库
def init__db():
    conn = pymysql.connect(
        host='localhost',
        user='root',
        password='5586305',
        db='pydb_movie250',
        charset='utf8'
    )
    cur = conn.cursor()
    try:
        create_sqli = "create table top25012 (id int not null primary key AUTO_INCREMENT,cname varchar(20),info_link text not null,pic_link text,bd text,tran text,score float,rated int);"
        cur.execute(create_sqli)
    except Exception as e:
        print("创建数据表失败:", e)
    else:
        print("创建数据表成功;")
    conn.commit()
    conn.close()


if __name__ == "__main__":
    # 初始化数据库
    # init__db()
    # 调用函数
    main()
