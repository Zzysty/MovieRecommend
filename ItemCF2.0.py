import csv
import random
import operator

import numpy as np
import pandas as pd


class ItemBasedCF:
    def __init__(self):
        self.N = {}  # 看过某部电影的用户数量
        self.W = {}  # 相似矩阵 存储电影i和j的相似度
        self.train = {}  # 训练集

        # 从最相似的k个已观看的电影中挑选n个电影进行推荐
        self.k = 30
        self.n = 10

    def get_data(self, file_path):
            # 从文件中加载数据
            print("开始加载数据...")
            with open(file_path, 'r') as f:
                for i, line in enumerate(f, 0):
                    line = line.strip("\r")
                    user, item, rating, timestamp = line.split(",")
                    self.train.setdefault(user, [])
                    self.train[user].append([item, rating])
            print("加载完毕！")

    def similarity(self):
            # 计算电影i和j之间的相似度
            print("开始计算相似度...")
            for user, item_ratings in self.train.items():
                items = [x[0] for x in item_ratings]
                for i in items:
                    self.N.setdefault(i, 0)
                    self.N[i] += 1
                    for j in items:
                        if i != j:
                            self.W.setdefault(i, {})
                            self.W[i].setdefault(j, 0)
                            self.W[i][j] += 1  # 同时看过电影i和j的用户数
            for i, j_cnt in self.W.items():
                for j, cnt in j_cnt.items():
                    self.W[i][j] = self.W[i][j] / (self.N[i] * self.N[j]) ** 0.5  # 电影i与电影j之间的相似度
            print("计算完毕！")

    def recommend(self, user):
            # 推荐用户user的电影
            print("开始为用户ID为", user, "的用户推荐电影...")
            rank = {}
            watched_items = [x[0] for x in self.train[user]]
            for i in watched_items:
                for j, similarity in sorted(self.W[i].items(), key=operator.itemgetter(1), reverse=True)[0:self.k]:
                    if j not in watched_items:
                        rank.setdefault(j, 0.)
                        rank[j] += float(self.train[user][watched_items.index(i)][1]) * similarity
            return sorted(rank.items(), key=operator.itemgetter(1), reverse=True)[0:self.n]

if __name__ == "__main__":
    file_path = "ratings.csv"
    itemBasedCF = ItemBasedCF()
    itemBasedCF.get_data(file_path)
    itemBasedCF.similarity()
    user = random.sample(list(itemBasedCF.train), 1)
    rec = itemBasedCF.recommend(user[0])
    print("\n被推荐电影的用户ID为", user[0], "为他推荐的电影有：")

    # 读取电影名称csv文件
    movies = pd.read_csv("movies.csv")
    movies = np.array(movies)

    # 遍历拿到推荐电影的movieID
    movieId = []
    for i in rec:
        # print(i[0])
         movieId.append(int(i[0]))

    # 遍历电影名称文件，找到推荐列表movieID对应的电影名称
    for item in movies:
        sh = int(item[0])
        if sh in movieId:
            print(item[1])