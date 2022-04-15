import pymysql
import distance     # 计算任意序列之间的相似性

def run_cal():
    db = pymysql.connect(host="localhost", port=3306, user="root",
                         passwd="5586305", db="movie", charset="utf8")
    cursor = db.cursor()
    sql = "select * from movies_movieinfo"
    cursor.execute(sql)     # execute 执行sql指令

    res = cursor.fetchall()     # 返回所有结果，二维元组形式，这里是所有电影信息
    id = 1
    print('\n\n cal_similar_gry.py\n\n')
    # 控制矩阵规模
    for i in range(0, len(res)):
        for j in range(i+1, len(res)):
            i_id = res[i][0]
            j_id = res[j][0]

            # 编辑距离 levenshtein 比较两个参数有几个相同个数
            moviename_length = distance.levenshtein(res[i][1], res[j][1])   # 电影名
            nation_length = distance.levenshtein(res[i][3], res[j][3])      # 国家
            directors_length = distance.levenshtein(res[i][4], res[j][4])   # 导演
            leadactors_length = distance.levenshtein(res[i][5], res[j][5])  # 主演
            # editors_length = distance.levenshtein(res[i][6], res[j][6])     # 编剧
            length = moviename_length + nation_length + \
                directors_length + leadactors_length       # 总长度

            similar = 1/length
            sql = "INSERT INTO movies_moviesimilar VALUES (%d, %d, %d, %f)" % (
                id, i_id, j_id, similar)
            try:
                cursor.execute(sql)
                db.commit()     # 提交
            except:
                db.rollback()   # 发生错误回滚
            id = id + 1
        print('current : ', i)
    db.close()
    print('DONE !')


if __name__ == '__main__':
    run_cal()
