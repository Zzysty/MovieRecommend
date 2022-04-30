#-*- coding: utf-8 -*-
'''
Created on 2022-04

@author: zzy
'''
import sys
import random
import math
import os
from operator import itemgetter

from collections import defaultdict

random.seed(0)


class ItemBasedCF(object):
    ''' TopN recommendation - Item Based Collaborative Filtering '''

    def __init__(self):
        self.trainset = {}
        self.testset = {}

        # 找到相似的20部电影，为目标用户推荐10部电影
        self.n_sim_movie = 20   # 相似的电影数量
        self.n_rec_movie = 8   # 推荐的电影数量

        self.movie_sim_mat = {}
        self.movie_popular = {}
        self.movie_count = 0    # 总电影数

        print('Similar movie number = %d' % self.n_sim_movie, file=sys.stderr)
        print('Recommended movie number = %d' % self.n_rec_movie, file=sys.stderr)

    @staticmethod
    def loadfile(filename):     # 加载文件
        ''' load a file, return a generator. '''    # 生成器
        fp =  open(filename, 'r')   # 打开文件
        for i, line in enumerate(fp):
            yield line.strip('\r\n')    # 去掉换行符
            if i % 100000 == 0:     # 每100000行输出一次
                print('loading %s(%s)' % (filename, i), file=sys.stderr)   # 输出到屏幕
        fp.close()   # 关闭文件
        print('load %s succ' % filename, file=sys.stderr)   # 输出到屏幕

    def generate_dataset(self, filename, pivot=0.7):    # 生成数据集
        ''' load rating data and split it to training set and test set '''  # 划分数据集
        trainset_len = 0    # 训练集长度
        testset_len = 0     # 测试集长度

        for line in self.loadfile(filename):
            user, movie, rating, _ = line.split('::')
            # split the data by pivot
            if random.random() < pivot:     # 划分数据集,小于0.7的数据为训练集
                self.trainset.setdefault(user, {})  # 创建字典
                self.trainset[user][movie] = int(rating)    # 字典中添加键值对
                trainset_len += 1    # 训练集长度加1
            else:
                self.testset.setdefault(user, {})    # 创建字典
                self.testset[user][movie] = int(rating)   # 字典中添加键值对
                testset_len += 1     # 测试集长度加1

        print ('split training set and test set succ', file=sys.stderr)
        print ('train set = %s' % trainset_len, file=sys.stderr)
        print ('test set = %s' % testset_len, file=sys.stderr)

    def calc_movie_sim(self):    # 计算电影相似度
        ''' calculate movie similarity matrix '''    # 计算电影相似度矩阵
        print('counting movies number and popularity...', file=sys.stderr)

        for user, movies in self.trainset.items():  # 遍历训练集
            for movie in movies:    # 遍历电影
                # count item popularity
                if movie not in self.movie_popular:    # 如果电影不在电影热度字典中
                    self.movie_popular[movie] = 0    # 则添加电影热度为0
                self.movie_popular[movie] += 1    # 电影热度加1

        print('count movies number and popularity succ', file=sys.stderr)

        # save the total number of movies
        self.movie_count = len(self.movie_popular)  # 电影总数
        print('total movie number = %d' % self.movie_count, file=sys.stderr)

        # count co-rated users between items
        itemsim_mat = self.movie_sim_mat     # 电影相似度矩阵
        print('building co-rated users matrix...', file=sys.stderr)

        for user, movies in self.trainset.items():  # 遍历训练集
            for m1 in movies:    # 遍历电影
                for m2 in movies:    # 遍历电影
                    if m1 == m2:    # 如果电影相同
                        continue    # 跳过
                    itemsim_mat.setdefault(m1, {})    # 创建字典
                    itemsim_mat[m1].setdefault(m2, 0)    # 创建字典
                    itemsim_mat[m1][m2] += 1    # 电影相似度加1

        print('build co-rated users matrix succ', file=sys.stderr)

        # calculate similarity matrix
        print('calculating movie similarity matrix...', file=sys.stderr)
        simfactor_count = 0   # 相似度计数
        PRINT_STEP = 2000000    # 每隔2000000次输出一次

        for m1, related_movies in itemsim_mat.items():  # 遍历电影相似度矩阵
            for m2, count in related_movies.items():    # 遍历电影相似度矩阵
                itemsim_mat[m1][m2] = count / math.sqrt(self.movie_popular[m1] * self.movie_popular[m2])    # 计算电影相似度
                simfactor_count += 1    # 相似度计数加1
                if simfactor_count % PRINT_STEP == 0:    # 每隔2000000次输出一次
                    print('calculating movie similarity factor(%d)' % simfactor_count, file=sys.stderr)

        print('calculate movie similarity matrix(similarity factor) succ',
              file=sys.stderr)
        print('Total similarity factor number = %d' %
              simfactor_count, file=sys.stderr)

    def recommend(self, user):  # 推荐
        ''' Find K similar movies and recommend N movies. '''    # 查找K个相似电影并推荐N部电影
        K = self.n_sim_movie    # K个相似电影
        N = self.n_rec_movie    # N部电影
        rank = {}    # 初始化推荐字典
        watched_movies = self.trainset[user]    # 获取用户观看的电影

        for movie, rating in watched_movies.items():    # 遍历用户观看的电影
            for related_movie, similarity_factor in sorted(self.movie_sim_mat[movie].items(),
                                                           key=itemgetter(1), reverse=True)[:K]:    # 遍历电影相似度矩阵
                if related_movie in watched_movies:    # 如果电影已经观看
                    continue    # 跳过
                rank.setdefault(related_movie, 0)    # 创建字典
                rank[related_movie] += similarity_factor * rating    # 相似度乘以电影评分
        # return the N best movies  # 返回N部电影
        return sorted(rank.items(), key=itemgetter(1), reverse=True)[:N]    # 按照评分排序

    def evaluate(self): # 评估
        ''' print evaluation result: precision, recall, coverage and popularity '''   # 输出评估结果
        print('Evaluation start...', file=sys.stderr)

        N = self.n_rec_movie    # N部电影
        #  varables for precision and recall
        hit = 0   # 命中
        rec_count = 0   # 推荐数
        test_count = 0   # 测试数
        # varables for coverage
        all_rec_movies = set()  # 所有推荐电影
        # varables for popularity
        popular_sum = 0  # 总的流行度

        for i, user in enumerate(self.trainset):    # 遍历训练集
            if i % 500 == 0:    # 每隔500次输出一次
                print('recommended for %d users' % i, file=sys.stderr)
            test_movies = self.testset.get(user, {})    # 获取用户测试集
            rec_movies = self.recommend(user)    # 获取用户推荐电影
            for movie, _ in rec_movies:    # 遍历推荐电影
                if movie in test_movies:    # 如果电影在测试集
                    hit += 1    # 命中加1
                all_rec_movies.add(movie)    # 所有推荐电影加1
                popular_sum += math.log(1 + self.movie_popular[movie])    # 流行度加1
            rec_count += N    # 推荐数加N
            test_count += len(test_movies)    # 测试数加电影数

        precision = hit / (1.0 * rec_count)   # 准确率
        recall = hit / (1.0 * test_count)   # 召回率
        coverage = len(all_rec_movies) / (1.0 * self.movie_count)    # 覆盖率
        popularity = popular_sum / (1.0 * rec_count)    # 流行度

        print ('precision=%.4f\trecall=%.4f\tcoverage=%.4f\tpopularity=%.4f' %
               (precision, recall, coverage, popularity), file=sys.stderr)


if __name__ == '__main__':
    ratingfile = os.path.join('ml-1m', 'ratings.dat')    # 评分文件
    itemcf = ItemBasedCF()  # 创建ItemBasedCF对象
    itemcf.generate_dataset(ratingfile)   # 生成数据集
    itemcf.calc_movie_sim()  # 计算电影相似度
    itemcf.evaluate()   # 评估
