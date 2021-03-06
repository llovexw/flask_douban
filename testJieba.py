# -*- coding = utf-8 -*-
# @Time:2021/04/01 22:44
# @Author:Luorui
# @File:testJieba.py
# @Software:PyCharm

import jieba            #分词
from matplotlib import pyplot as plt    #数据可视化绘图
from wordcloud import WordCloud         #词云
from PIL import Image                   #图片处理
import numpy as np                      #矩阵运算
import sqlite3

#准备词云所需的文字
con = sqlite3.connect('movie.db')
cur = con.cursor()
sql = 'select introduction from movieTop250'
data = cur.execute(sql)
text = ''
for item in data:
    text = text + item[0]

#print(text)

cur.close()
con.close()

cut = jieba.cut(text)
string = ' '.join(cut)
print(len(string))

img = Image.open(r'.\static\assets\img\tree.jpg') #打开遮罩图片
img_array = np.array(img)    #将图片转换为数组
wc = WordCloud(
    background_color='white',
    mask=img_array,
    font_path='simkai.ttf',
)

wc.generate_from_text(string)


#绘制图片
fig  = plt.figure(1)
plt.imshow(wc)
plt.axis('off') #是否显示坐标轴

#plt.show()     #显示生成的词云图片
plt.savefig(r'.\static\assets\img\word2.jpg',dpi=600)