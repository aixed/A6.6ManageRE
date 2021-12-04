

# 配置 A++ 6.6 数据库连接信息
# HOST = '10.11.0.37'
# PORT = '5324'
# USERNAME = 'xzsijjcw2019'
# PASSWORD = 'xzsijjcw2021'
# DATABASE = 'xzrsjjcw'

HOST = '10.11.0.37'
PORT = '5212'
USERNAME = 'AIXED_20211111'
PASSWORD = 'xzsijjcw'
DATABASE = 'xzrszjk'

SQLALCHEMY_DATABASE_URI = "oracle://{username}:{password}@{host}:{port}/{db}".format(username=USERNAME,
                                                                                        password=PASSWORD,
                                                                                        host=HOST, port=PORT,
                                                                                        db=DATABASE)

# 设置是否跟踪数据库的修改情况，一般不跟踪
SQLALCHEMY_TRACK_MODIFICATIONS = False
# 数据库操作时是否显示原始SQL语句，一般都是打开的，因为我们后台要日志
SQLALCHEMY_ECHO = False



