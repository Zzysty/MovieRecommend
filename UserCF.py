import sys
import random
import math
import os
from operator import itemgetter 

from collections import defaultdict     

# seed() 用于指定随机数生成时所用算法开始的整数值。
# 1.如果使用相同的seed()值，则每次生成的随即数都相同；
# 2.如果不设置这个值，则系统根据时间来自己选择这个值，此时每次生成的随机数因时间差异而不同。
# 3.设置的seed()值一直有效
random.seed(0)  # 设置随机数种子


class UserBasedCF(object):  # 用户相似度算法
    ''' TopN recommendation - User Based Collaborative Filtering '''    

    def __init__(self): 
        self.trainset = {}  # train set
        self.testset = {}   # test set

         # 找到与目标用户兴趣相似的20个用户，为其推荐n部电影
        self.n_sim_user = 20    # number of similar users to recommend
        self.n_rec_movie = 16    # number of recommendation

        self.user_sim_mat = {}  
        self.movie_popular = {}
        self.movie_count = 0

        print ('Similar user number = %d' % self.n_sim_user, file=sys.stderr)
        print ('recommended movie number = %d' %
               self.n_rec_movie, file=sys.stderr)

    @staticmethod   
    def loadfile(filename): # 加载文件
        ''' load a file, return a generator. '''
        fp = open(filename, 'r')    # 读取文件
        for i, line in enumerate(fp):   # 返回文件行数
            yield line.strip('\r\n')    # 去除换行符
            if i % 100000 == 0:  # 每100000行输出一次
                print ('loading %s(%s)' % (filename, i), file=sys.stderr)
        fp.close()
        print ('load %s succ' % filename, file=sys.stderr)

    # 读文件得到“用户-电影”数据
    def generate_dataset(self, filename, pivot=0.7):    # 生成数据集
        ''' load rating data and split it to training set and test set '''
        trainset_len = 0    # 训练集长度
        testset_len = 0    # 测试集长度

        for line in self.loadfile(filename):    # 加载文件
            user, movie, rating, _ = line.split('::')   # 分割字符串
            # split the data by pivot
            if random.random() < pivot:   # 随机数小于pivot=0.7
                self.trainset.setdefault(user, {})  # 创建字典
                self.trainset[user][movie] = int(rating)    # 设置字典
                trainset_len += 1   # 训练集长度加1
            else:   # 随机数大于pivot=0.7
                self.testset.setdefault(user, {})   # 创建字典
                self.testset[user][movie] = int(rating)  # 设置字典
                testset_len += 1    # 测试集长度加1

        print ('split training set and test set succ', file=sys.stderr)
        print ('train set = %s' % trainset_len, file=sys.stderr)
        print ('test set = %s' % testset_len, file=sys.stderr)

    def calc_user_sim(self):    # 计算用户相似度
        ''' calculate user similarity matrix '''
        # build inverse table for item-users
        # key=movieID, value=list of userIDs who have seen this movie
        print ('building movie-users inverse table...', file=sys.stderr)
        movie2users = dict()    

        for user, movies in self.trainset.items():  # 循环训练集
            for movie in movies:    # 循环用户的电影
                # inverse table for item-users
                if movie not in movie2users:    # 如果电影不在电影列表中
                    movie2users[movie] = set()  # 创建电影列表
                movie2users[movie].add(user)    # 将用户添加到电影列表中
                # count item popularity at the same time    
                if movie not in self.movie_popular:   # 如果电影不在电影热度列表中
                    self.movie_popular[movie] = 0   # 创建电影热度列表
                self.movie_popular[movie] += 1  # 电影热度加1
        print ('build movie-users inverse table succ', file=sys.stderr)

        # save the total movie number, which will be used in evaluation
        self.movie_count = len(movie2users)   # 电影总数
        print ('total movie number = %d' % self.movie_count, file=sys.stderr)

        # count co-rated items between users
        usersim_mat = self.user_sim_mat     # 用户相似度矩阵
        print ('building user co-rated movies matrix...', file=sys.stderr)

        for movie, users in movie2users.items():    # 循环电影列表
            for u in users:  # 循环用户列表
                usersim_mat.setdefault(u, defaultdict(int)) # 创建用户相似度字典
                for v in users: # 循环用户列表
                    if u == v:  # 如果用户相同
                        continue    # 跳过
                    usersim_mat[u][v] += 1  # 用户相似度加1
        print ('build user co-rated movies matrix succ', file=sys.stderr)

        # calculate similarity matrix
        print ('calculating user similarity matrix...', file=sys.stderr)
        simfactor_count = 0  # 相似度计数
        PRINT_STEP = 2000000    # 每隔2000000次输出一次

        for u, related_users in usersim_mat.items():    # 循环用户列表 
            for v, count in related_users.items():  # 循环用户列表
                usersim_mat[u][v] = count / math.sqrt(  # 计算用户相似度
                    len(self.trainset[u]) * len(self.trainset[v]))  
                simfactor_count += 1    # 相似度计数加1
                if simfactor_count % PRINT_STEP == 0:   # 每隔2000000次输出一次
                    print ('calculating user similarity factor(%d)' %
                           simfactor_count, file=sys.stderr)

        print ('calculate user similarity matrix(similarity factor) succ',
               file=sys.stderr)
        print ('Total similarity factor number = %d' %
               simfactor_count, file=sys.stderr)

    def recommend(self, user):  # 推荐
        ''' Find K similar users and recommend N movies. '''
        K = self.n_sim_user  # K个相似用户
        N = self.n_rec_movie    # N个推荐电影
        rank = dict()   # 创建字典
        watched_movies = self.trainset[user]    # 获取用户观看的电影

        for similar_user, similarity_factor in sorted(self.user_sim_mat[user].items(),  
                                                      key=itemgetter(1), reverse=True)[0:K]:
            for movie in self.trainset[similar_user]:   
                if movie in watched_movies:   # 如果电影已经观看
                    continue
                # predict the user's "interest" for each movie
                rank.setdefault(movie, 0)   
                rank[movie] += similarity_factor    # 用户相似度加1
        # return the N best movies
        return sorted(rank.items(), key=itemgetter(1), reverse=True)[0:N]

    def evaluate(self):
        ''' print evaluation result: precision, recall, coverage and popularity '''
        print ('Evaluation start...', file=sys.stderr)

        N = self.n_rec_movie    # N个推荐电影
        #  varables for precision and recall
        hit = 0   # 推荐准确数
        rec_count = 0   # 推荐总数
        test_count = 0   # 测试总数
        # varables for coverage
        all_rec_movies = set()   # 所有推荐电影
        # varables for popularity
        popular_sum = 0  # 所有电影总的流行度

        for i, user in enumerate(self.trainset):    # 循环用户列表
            if i % 500 == 0:
                print ('recommended for %d users' % i, file=sys.stderr)
            test_movies = self.testset.get(user, {})  # 获取用户测试电影
            rec_movies = self.recommend(user)  # 推荐
            for movie, _ in rec_movies:  # 循环推荐电影
                if movie in test_movies:   # 如果电影已经测试
                    hit += 1  # 推荐准确数加1
                all_rec_movies.add(movie)  # 所有推荐电影加1
                popular_sum += math.log(1 + self.movie_popular[movie])  # 流行度加1
            rec_count += N    # 推荐总数加N
            test_count += len(test_movies)  # 测试总数加1

        precision = hit / (1.0 * rec_count)  # 推荐准确率
        recall = hit / (1.0 * test_count)    # 推荐召回率
        coverage = len(all_rec_movies) / (1.0 * self.movie_count)
        popularity = popular_sum / (1.0 * rec_count)

        print ('precision=%.4f\trecall=%.4f\tcoverage=%.4f\tpopularity=%.4f' %
               (precision, recall, coverage, popularity), file=sys.stderr)


if __name__ == '__main__':
    ratingfile = os.path.join('ml-1m', 'ratings.dat')
    usercf = UserBasedCF()
    usercf.generate_dataset(ratingfile)
    usercf.calc_user_sim()
    usercf.evaluate()
