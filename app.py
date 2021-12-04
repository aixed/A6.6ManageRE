import json
import hashlib
import cx_Oracle
import numpy as np
from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
from flask_httpauth import HTTPBasicAuth
from flask_sqlalchemy import SQLAlchemy
import database_config
from Json_Return import *

app = Flask(__name__)

# 从文件加载数据库配置信息
app.config.from_object(database_config)
# 连接数据库
# app.config['SQLALCHEMY_DATABASE_URI'] = 'oracle://xzsijjcw2019:xzsijjcw@10.11.0.37:5324/xzrsjjcw'


# 实例化orm框架的操作对象，后续数据库操作，都要基于操作对象来完成
db = SQLAlchemy(app)


@app.route('/')
def moren():
    return 'QQ:364831018'


# 用户登陆
@app.route('/api/user/login', methods=["POST"])
def login():
    if request.method == 'POST':

        # 取所有类型  用这个 下面那个 报错
        username = request.values.get('username')
        password = request.values.get("password")
        if username == None or password == None:
            # json 格式的数据
            reqParm = json.loads(request.data.decode())
            username = reqParm['username']
            password = reqParm['password']
            print('[收到Json格式数据]', 'username', username, 'password', password)

        print('[POST] 用户:', username)
        print('[POST] 密码:', password)

        if username == None:
            print('用户名错误')
            return '用户名或密码错误'

        elif password == None:
            print('密码错误')
            return '用户名或密码错误'

        else:

            sql = "select passwd from as_user t where user_code='" + username + "'"
            data = db.session.execute(sql)

            rows = data.fetchone()
            print('获取完成：数据条目', rows, '第一条数据：', rows[0])

            hash_pwd = hashlib.md5()
            hash_pwd.update(password.encode("utf-8"))
            passwd_md5 = hash_pwd.hexdigest()

            print('发送过来的密码加密后', passwd_md5)

            print('数据库中的密码', rows[0])

            if passwd_md5 == rows[0]:
                return '登陆成功'
            else:
                return '账号或密码错误，登陆失败！'

    else:
        return jsonify("错误")


# 登陆情况
@app.route("/api/InfoQuery/LoginList", methods=['GET'])
def 信息查询_登陆情况():
    if request.method == 'GET':

        page_size = request.values.get('Page_Size')
        page_size = int(page_size)
        cur_pagenum = request.values.get('cur_PageNum')
        cur_pagenum = int(cur_pagenum)

        print('[GET] 当前页面显示条数:', page_size)
        print('[GET] 当前选择第几页:', cur_pagenum)

        if page_size == '' or page_size == None:
            return jsonify("无数据")

        if cur_pagenum == 1:
            startrow = '0'
            endrow = page_size

        elif cur_pagenum > 1:
            startrow = page_size * (cur_pagenum -1)
            endrow = startrow + page_size

        else:
            startrow = '0'
            endrow = page_size

        conutsql = "select count(*) from V_BASE_USER_LOGIN_ONLY t"
        alllen = db.session.execute(conutsql)
        rows_ = alllen.fetchall()
        for (all_inc,) in rows_:
            print('总数：', all_inc)


        db.session.close()

        # SELECT * FROM (SELECT ROWNUM AS rowno, t.* FROM V_BASE_USER_LOGIN_ONLY t  WHERE  ROWNUM <= 20) t WHERE t.rowno > 10;
        sql = "SELECT * FROM (SELECT ROWNUM AS rowno, t.* FROM V_BASE_USER_LOGIN_ONLY t  WHERE  ROWNUM <= " + str(
            endrow) + ") t WHERE t.rowno > " + str(startrow) + ""

        data = db.session.execute(sql)
        rows = data.fetchall()


        print('查询到：' + str(len(rows)) + '条数据！')

        if len(rows) == 0:
            return jsonify("无数据")

        i = 1
        temp = {}
        result = []
        result_all = {}
        head = {
            "total": all_inc,
            "pageSize": page_size,
            "curPageNum": cur_pagenum,
        }

        for row in rows:
            temp["ROWNO"] = row[0]
            temp["USER_ID"] = row[1]
            temp["Ipaddr"] = row[2]
            temp["LoginTime"] = row[3]
            temp["LoginOutTime"] = row[4]

            i = i + 1
            result.append(temp.copy())

        # Z_dict = dict(list(a.items()) + [('b1', 'b2')])

        # print(result)
        # c = '{"config":' + str(res) + "," + '"data":' + str(result) + '}'
        # c = c.replace("'", '"')
        # print(c)
        result_all["config"] = head
        result_all["data"] = result
        return jsonify(result_all)




    else:
        return jsonify("请求方式错误")


# 查询.在线统计
@app.route("/api/InfoQuery/OnlineStatistics", methods=['GET'])
def 信息查询_在线统计():
    if request.method == 'GET':

        # select t.USER_ID, u.USER_NAME, t.IP, t.CREATE_TIME, aus1.session_value as CO_CODE, aus2.session_value as CO_NAME from AS_USER_TICKET t
        # left join AS_USER u    on t.user_id = u.user_id
        # left join AS_USER_SESSION aus1    on t.user_id = aus1.user_id   and aus1.session_key = 'svCoCode'
        # left join AS_USER_SESSION aus2    on aus2.user_id = t.user_id   and aus2.session_key = 'svCoName'
        # order by USER_ID, CREATE_TIME

        sql = "select * from V_BASE_USER_ONLINETIME"

        print(sql)

        data = db.session.execute(sql)
        db.session.commit()
        rows = data.fetchall()
        print("总行数:", len(rows))
        if len(rows) == 0:
            return jsonify("无数据")
        i = 1
        temp = {}
        result = []
        for row in rows:
            temp["USER_ID"] = row[0]
            temp["USER_NAME"] = row[1]
            temp["IP"] = row[2]
            temp["CREATE_TIME"] = row[3]
            temp["ONLINE_TIME"] = row[4]
            temp["CO_CODE"] = row[5]
            temp["CO_NAME"] = row[6]

            # print("row:", i, row[0], row[1], row[2], row[3])
            i = i + 1
            result.append(temp.copy())

        return jsonify(result)

    else:
        return jsonify("请求方式错误")


# 查询.全区所有单位
@app.route("/api/InfoQuery/ALL_Unit", methods=['GET'])
def 信息查询_全区所有单位():
    if request.method == 'GET':

        co_name = request.values.get('co_name')

        print('[GET] 传入单位名称:', co_name)

        if co_name == '':
            sql = "select co_code,co_name,parent_co_code,is_lowest from V_BASE_MA_COMPANY t order by co_code"
        else:
            sql = "select co_code,co_name,parent_co_code,is_lowest from V_BASE_MA_COMPANY t where co_name like '%" \
                  + co_name + "%' " \
                              "order by co_code"

        print(sql)

        data = db.session.execute(sql)
        db.session.commit()
        rows = data.fetchall()
        print("总行数:", len(rows))
        if len(rows) == 0:
            return jsonify("无数据")
        i = 1
        temp = {}
        result = []
        for row in rows:
            temp["CO_CODE"] = row[0]
            temp["CO_NAME"] = row[1]
            temp["PARENT_CO_CODE"] = row[2]
            temp["IS_LOWEST"] = row[3]

            # print("row:", i, row[0], row[1], row[2], row[3])
            i = i + 1
            result.append(temp.copy())

        return jsonify(result)

    else:
        return jsonify("请求方式错误")


# 查询.操作日志
@app.route("/api/InfoQuery/operlog", methods=['GET'])
def 信息查询_操作日志():
    if request.method == 'GET':

        # select oper_time,user_id,user_name,compo_id,compo_name,oper_desc,user_ip,mac_address
        # from V_BASE_AS_LOG t
        # where oper_time between '2021-02-08' and '2021-02-16' or oper_time between '20210208' and '20210216'
        # order by oper_time desc

        start_date = request.values.get('start_date')
        end_date = request.values.get("end_date")

        print('[GET] 起始时间:', start_date)
        print('[GET] 结束时间:', end_date)

        start_date = start_date[0:10]
        end_date = end_date[0:10]

        print('[GET] 起始时间:', start_date)
        print('[GET] 结束时间:', end_date)

        start_date_ = start_date[0:4] + start_date[6:2] + start_date[9:2]
        end_date_ = end_date[0:4] + end_date[5:2] + end_date[7:2]

        sql = "select oper_time,user_id,user_name,compo_id,compo_name,oper_desc,user_ip,mac_address " \
              "from V_BASE_AS_LOG t " \
              "where oper_time between " + "'" + start_date + "'" + " and " + "'" + end_date + "'" \
              + " union all " \
              + "select oper_time,user_id,user_name,compo_id,compo_name,oper_desc,user_ip,mac_address " \
                "from V_BASE_AS_LOG t " \
              + "where oper_time between '" + start_date_ + "' and '" + end_date_ + "' order by oper_time desc"

        print('sql', sql)

        data = db.session.execute(sql)
        db.session.commit()
        rows = data.fetchall()
        print("总行数:", len(rows))
        if len(rows) == 0:
            return jsonify("无数据")

        i = 1
        temp = {}
        result = []
        for row in rows:
            temp["OPER_TIME"] = row[0]
            temp["USER_ID"] = row[1]
            temp["USER_NAME"] = row[2]
            temp["COMPO_ID"] = row[3]
            temp["COMPO_NAME"] = row[4]
            temp["OPER_DESC"] = row[5]
            temp["USER_IP"] = row[6]
            temp["MAC_ADDRESS"] = row[7]

            # print("row:", i, row[0], row[1], row[2], row[3])
            i = i + 1
            result.append(temp.copy())

        return jsonify(result)

    else:
        return jsonify("请求方式错误")


# 查询.余额汇总表
@app.route('/api/InfoQuery/yehzb', methods=['GET'])
def 查询余额汇总表():
    if request.method == "GET":

        # 取所有类型  用这个 下面那个 报错
        nd = request.values.get('nd')
        zt = request.values.get("zt")
        dw = request.values.get("dw")
        month_start = request.values.get("month_start")
        month_end = request.values.get("month_end")
        having_nj = request.values.get("delivery")

        print('[GET] 年度:', nd)
        print('[GET] 账套:', zt)
        print('[GET] 单位:', dw)
        print('[GET] 起始月份:', month_start, type(month_start))
        print('[GET] 结束月份:', month_end, type(month_end))
        print('[GET] 是否包含年结凭证:', having_nj, type(having_nj))

        if nd == '' and zt == '':
            result = []
            temp = {
                    'ND': '',
                    'CO_CODE': '',
                    'CO_NAME': '',
                    'ACCOUNT_ID':'',
                    'ACCOUNT_NAME': '',
                    'ACC_CODE': '',
                    'ACC_NAME': '',
                    'QCYE_JF': '',
                    'QCYE_DF': '',
                    'BQFS_JF': '',
                    'BQFS_DF': '',
                    'LJFS_JF': '',
                    'LJFS_DF': '',
                    'QMYE_JF': '',
                    'QMYE_DF': '',
            }
            result.append(temp)
            temp = {}
            return jsonify('')


#
# select * from
# (
# select
# a."年度",a."单位代码",a."单位名称",a."账套代码",a."账套名称",a."科目代码",a."科目名称",
# a."期初余额_借方",
# a."期初余额_贷方",
# a."本期发生_借方",a."本期发生_贷方",a."累计发生_借方",a."累计发生_贷方",
# (case
#   when sum(期末余额_借方)-sum(期末余额_贷方) >0 then
#     sum(期末余额_借方)-sum(期末余额_贷方)
# end) 期末余额_借方,
# (case
#   when sum(期末余额_贷方)-sum(期末余额_借方) >0 then
#     sum(期末余额_贷方)-sum(期末余额_借方)
# end) 期末余额_贷方
# from
# (
# select
# a.*,
# sum(c.累计发生_借方) 累计发生_借方,
# sum(c.累计发生_贷方) 累计发生_贷方
# from
# (
# select
# a."年度",a."单位代码",a."单位名称",a."账套代码",a."账套名称",a."科目代码",a."科目名称",a.期初余额_借方,a.期初余额_贷方,
# sum(d.本期发生_借方) 本期发生_借方,
# sum(d.本期发生_贷方) 本期发生_贷方
# from
# (
# select
# a."年度",a."单位代码",a."单位名称",a."账套代码",a."账套名称",a."科目代码",a."科目名称",
# (case
#   when sum(b.期初余额_借方)-sum(b.期初余额_贷方) >0 then
#     sum(b.期初余额_借方)-sum(b.期初余额_贷方)
# end) 期初余额_借方,
# (case
#   when sum(b.期初余额_贷方)-sum(b.期初余额_借方) >0 then
#     sum(b.期初余额_贷方)-sum(b.期初余额_借方)
# end) 期初余额_贷方
# from V_BASE_ALLUNIT_余额表_通用字段 a
# left join V_BASE_ALLUNIT_期初余额 b on  b.年度=a.年度 and b.单位代码=a.单位代码 and b.账套代码=a.账套代码 and b.科目代码=a.科目代码 and b.会计期间 between 0 and 3
# group by a.年度,a.单位代码,a.单位名称,a.账套代码,a.账套名称,a.科目代码,a.科目名称
# order by a.科目代码
# ) a
# left join V_BASE_ALLUNIT_本期发生 d on  d.年度=a.年度 and d.单位代码=a.单位代码 and d.账套代码=a.账套代码 and d.科目代码=a.科目代码 and d.会计期间 in(4,5)
# group by a.年度,a.单位代码,a.单位名称,a.账套代码,a.账套名称,a.科目代码,a.科目名称,a.期初余额_借方,a.期初余额_贷方
# order by a.科目代码
# ) a
# left join V_BASE_ALLUNIT_累计发生 c on  c.年度=a.年度 and c.单位代码=a.单位代码 and c.账套代码=a.账套代码 and c.科目代码=a.科目代码 and c.会计期间 between 1 and 5
# group by a.年度,a.单位代码,a.单位名称,a.账套代码,a.账套名称,a.科目代码,a.科目名称,a.期初余额_借方,a.期初余额_贷方,a.本期发生_借方,a.本期发生_贷方
# order by a.科目代码
# )a
# left join V_BASE_ALLUNIT_期末余额 d on  d.年度=a.年度 and d.单位代码=a.单位代码 and d.账套代码=a.账套代码 and d.科目代码=a.科目代码 and d.会计期间 between 0 and 5
# group by a.年度,a.单位代码,a.单位名称,a.账套代码,a.账套名称,a.科目代码,a.科目名称,a.期初余额_借方,a.期初余额_贷方,a.本期发生_借方,a.本期发生_贷方,a.累计发生_借方,a.累计发生_贷方
# order by a.科目代码
# )
# where 单位代码=549900001 and 年度=2021 and 账套代码=111 and 科目代码 like '100302%'
# ;
        month_start_qc = str(int(month_start) - 1)
        if having_nj == 'true':
            pass

            sql_1 = """
                select 年度,单位代码,单位名称,账套代码,账套名称,科目代码,科目名称,
                case 
                when instr(to_char(期初余额_借方), '.') < 1 and 期初余额_借方 is not null then 期初余额_借方 | | '.00'
                when instr(to_char(期初余额_借方), '.') + 1 = length(期初余额_借方) and 期初余额_借方 is not null then 期初余额_借方 | | '0'
                when 期初余额_借方 is null then null
                else to_char(round(期初余额_借方, 2))
                end 期初余额_借方,
                case
                when instr(to_char(期初余额_贷方), '.') < 1 and 期初余额_贷方 is not null then 期初余额_贷方 | | '.00'
                when instr(to_char(期初余额_贷方), '.') + 1 = length(期初余额_贷方) and 期初余额_贷方 is not null then 期初余额_贷方 | | '0'
                when 期初余额_贷方 is null then null
                else to_char(round(期初余额_贷方, 2))
                end 期初余额_贷方,
                本期发生_借方, 本期发生_贷方, 累计发生_借方, 累计发生_贷方, 
                
                case 
                when instr(to_char(期末余额_借方), '.') < 1 and 期末余额_借方 is not null then 期末余额_借方 | | '.00'
                when instr(to_char(期末余额_借方), '.') + 1 = length(期末余额_借方) and 期末余额_借方 is not null then 期末余额_借方 | | '0'
                when 期末余额_借方 is null then null
                else to_char(round(期末余额_借方, 2))
                end 期末余额_借方,
                """
            sql_2 = """
                case
                when instr(to_char(期末余额_贷方), '.') < 1 and 期末余额_贷方 is not null then 期末余额_贷方 | | '.00'
                when instr(to_char(期末余额_贷方), '.') + 1 = length(期末余额_贷方) and 期末余额_贷方 is not null then 期末余额_贷方 | | '0'
                when 期末余额_贷方 is null then null
                else to_char(round(期末余额_贷方, 2))
                end 期末余额_贷方
                 from (select a.年度,a.单位代码,a.单位名称,a.账套代码,a.账套名称,a.科目代码,a.科目名称, 
                a.期初余额_借方, a.期初余额_贷方,
                
                case 
                when instr(to_char(a.本期发生_借方), '.') < 1 and a.本期发生_借方 != 0 then a.本期发生_借方 || '.00' 
                when instr(to_char(a.本期发生_借方), '.') + 1 = length(a.本期发生_借方) and a.本期发生_借方 != 0 then a.本期发生_借方 || '0' 
                when a.本期发生_借方 = 0 then '' 
                else 
                to_char(round(a.本期发生_借方, 2)) 
                end 本期发生_借方, 
                case 
                when instr(to_char(a.本期发生_贷方), '.') < 1 and a.本期发生_贷方 != 0 then a.本期发生_贷方 | | '.00' 
                when instr(to_char(a.本期发生_贷方), '.') + 1 = length(a.本期发生_贷方) and a.本期发生_贷方 != 0 then a.本期发生_贷方 | | '0' 
                when a.本期发生_贷方 = 0 then '' 
                else 
                to_char(round(a.本期发生_贷方, 2)) 
                end 本期发生_贷方, 
                case 
                when instr(to_char(a.累计发生_借方), '.') < 1 and a.累计发生_借方 != 0 then a.累计发生_借方 | | '.00' 
                when instr(to_char(a.累计发生_借方), '.') + 1 = length(a.累计发生_借方) and a.累计发生_借方 != 0 then a.累计发生_借方 | | '0' 
                when a.累计发生_借方 = 0 then '' 
                else 
                to_char(round(a.累计发生_借方, 2)) 
                end 累计发生_借方, 
                case 
                when instr(to_char(a.累计发生_贷方), '.') < 1 and a.累计发生_贷方 != 0 then a.累计发生_贷方 | | '.00' 
                when instr(to_char(a.累计发生_贷方), '.') + 1 = length(a.累计发生_贷方) and a.累计发生_贷方 != 0 then a.累计发生_贷方 | | '0' 
                when a.累计发生_贷方 = 0 then '' 
                
                else 
                to_char(round(a.累计发生_贷方, 2)) 
                end 累计发生_贷方, 
                (case 
                  when sum(期末余额_借方)-sum(期末余额_贷方) >0 then 
                    sum(期末余额_借方)-sum(期末余额_贷方) 
                end) 期末余额_借方, 
                (case 
                  when sum(期末余额_贷方)-sum(期末余额_借方) >0 then 
                    sum(期末余额_贷方)-sum(期末余额_借方) 
                end) 期末余额_贷方 
                 from  
                ( 
                select  
                a.*, 
                sum(c.累计发生_借方) 累计发生_借方, sum(c.累计发生_贷方) 累计发生_贷方 
                 from 
                ( 
                select  
                a."年度",a."单位代码",a."单位名称",a."账套代码",a."账套名称",a."科目代码",a."科目名称",a.期初余额_借方,a.期初余额_贷方, 
                sum(d.本期发生_借方) 本期发生_借方, 
                sum(d.本期发生_贷方) 本期发生_贷方 
                 from  
                ( 
                select 
                a.年度,a.单位代码,a.单位名称,a.账套代码,a.账套名称,a.科目代码,a.科目名称, 
                (case 
                  when sum(b.期初余额_借方)-sum(b.期初余额_贷方) >0 then 
                    sum(b.期初余额_借方)-sum(b.期初余额_贷方) 
                end) 期初余额_借方, 
                (case 
                  when sum(b.期初余额_贷方)-sum(b.期初余额_借方) >0 then 
                    sum(b.期初余额_贷方)-sum(b.期初余额_借方) 
                end) 期初余额_贷方 
                from V_BASE_ALLUNIT_余额表_通用字段 a 
                """
            sql_3 = """
                left join V_BASE_ALLUNIT_期初余额 b on  b.年度=a.年度 and b.单位代码=a.单位代码 and b.账套代码=a.账套代码 and b.科目代码=a.科目代码 and b.会计期间 between 0 and """ + month_start_qc + """
                group by a.年度,a.单位代码,a.单位名称,a.账套代码,a.账套名称,a.科目代码,a.科目名称 
                order by a.科目代码 
                ) a 
                left join V_BASE_本期发生_包含年结 d on  d.年度=a.年度 and d.单位代码=a.单位代码 and d.账套代码=a.账套代码 and d.科目代码=a.科目代码 and d.会计期间 in(""" + month_start + """,""" + month_end + """) 
                group by a.年度,a.单位代码,a.单位名称,a.账套代码,a.账套名称,a.科目代码,a.科目名称,a.期初余额_借方,a.期初余额_贷方 
                order by a.科目代码 
                ) a 
                left join V_BASE_累计发生_包含年结 c on  c.年度=a.年度 and c.单位代码=a.单位代码 and c.账套代码=a.账套代码 and c.科目代码=a.科目代码 and c.会计期间 between 1 and """ + month_end + """ 
                group by a.年度,a.单位代码,a.单位名称,a.账套代码,a.账套名称,a.科目代码,a.科目名称,a.期初余额_借方,a.期初余额_贷方,a.本期发生_借方,a.本期发生_贷方 
                order by a.科目代码 
                )a 
                left join V_BASE_期末余额_包含年结 d on  d.年度=a.年度 and d.单位代码=a.单位代码 and d.账套代码=a.账套代码 and d.科目代码=a.科目代码 and d.会计期间 between 0 and """ + month_end + """
                group by a.年度,a.单位代码,a.单位名称,a.账套代码,a.账套名称,a.科目代码,a.科目名称,a.期初余额_借方,a.期初余额_贷方,a.本期发生_借方,a.本期发生_贷方,a.累计发生_借方,a.累计发生_贷方 
                order by a.科目代码 
                ) 
                """

            if dw == '':

                sql_0 = """
                select 年度,'' 单位代码,'' 单位名称,账套代码,'' 账套名称,科目代码,科目名称,期初余额_借方,期初余额_贷方,本期发生_借方,本期发生_贷方,累计发生_借方,累计发生_贷方,期末余额_借方,期末余额_贷方
                from (
                select 年度,账套代码,科目代码,科目名称,sum(期初余额_借方) 期初余额_借方,sum(期初余额_贷方) 期初余额_贷方,sum(本期发生_借方) 本期发生_借方,sum(本期发生_贷方) 本期发生_贷方,sum(累计发生_借方) 累计发生_借方,sum(累计发生_贷方) 累计发生_贷方,sum(期末余额_借方) 期末余额_借方,sum(期末余额_贷方) 期末余额_贷方
                     from 
                     (
                     """

                sql_4 = """
                     where 单位代码 in ('549900001','540199001','540299001','540399001','540499001','540599001','540699001','542599001')""" + """ and 年度='""" + nd + """' and 账套代码='""" + zt + """'""" + """
                         ) a
                         group by 年度,账套代码,科目代码,科目名称
                         order by 科目代码
                         )
                     """
            else:
                sql_0 = ''

                sql_4 = """where 单位代码='""" + dw + """' and 年度='""" + nd + """' and 账套代码='""" + zt + """'
                """

            sql = sql_0 + sql_1 + sql_2 + sql_3 + sql_4
            #print("sql 语句: 1", sql)
        else:
            pass

            sql = "select 年度,单位代码,单位名称,账套代码,账套名称,科目代码,科目名称,\n" \
                "case \n" \
                "when instr(to_char(期初余额_借方), '.') < 1 and 期初余额_借方 is not null then 期初余额_借方 | | '.00'\n" \
                "when instr(to_char(期初余额_借方), '.') + 1 = length(期初余额_借方) and 期初余额_借方 is not null then 期初余额_借方 | | '0'\n" \
                "when 期初余额_借方 is null then null\n" \
                "else to_char(round(期初余额_借方, 2))\n" \
                "end 期初余额_借方,\n" \
                "case\n" \
                "when instr(to_char(期初余额_贷方), '.') < 1 and 期初余额_贷方 is not null then 期初余额_贷方 | | '.00'\n" \
                "when instr(to_char(期初余额_贷方), '.') + 1 = length(期初余额_贷方) and 期初余额_贷方 is not null then 期初余额_贷方 | | '0'\n" \
                "when 期初余额_贷方 is null then null\n" \
                "else to_char(round(期初余额_贷方, 2))\n" \
                "end 期初余额_贷方,\n" \
                "本期发生_借方, 本期发生_贷方, 累计发生_借方, 累计发生_贷方, " \
                "case \n" \
                "when instr(to_char(期末余额_借方), '.') < 1 and 期末余额_借方 is not null then 期末余额_借方 | | '.00'\n" \
                "when instr(to_char(期末余额_借方), '.') + 1 = length(期末余额_借方) and 期末余额_借方 is not null then 期末余额_借方 | | '0'\n" \
                "when 期末余额_借方 is null then null\n" \
                "else to_char(round(期末余额_借方, 2))\n" \
                "end 期末余额_借方,\n" \
                "case\n" \
                "when instr(to_char(期末余额_贷方), '.') < 1 and 期末余额_贷方 is not null then 期末余额_贷方 | | '.00'\n" \
                "when instr(to_char(期末余额_贷方), '.') + 1 = length(期末余额_贷方) and 期末余额_贷方 is not null then 期末余额_贷方 | | '0'\n" \
                "when 期末余额_贷方 is null then null\n" \
                "else to_char(round(期末余额_贷方, 2))\n" \
                "end 期末余额_贷方\n" \
              " from " \
                "(" \
                "select " \
                "a.年度,a.单位代码,a.单位名称,a.账套代码,a.账套名称,a.科目代码,a.科目名称, \n" \
                "a.期初余额_借方, a.期初余额_贷方,\n" \
                "case \n" \
                "when instr(to_char(a.本期发生_借方), '.') < 1 and a.本期发生_借方 != 0 then a.本期发生_借方 || '.00' \n" \
                "when instr(to_char(a.本期发生_借方), '.') + 1 = length(a.本期发生_借方) and a.本期发生_借方 != 0 then a.本期发生_借方 || '0' \n" \
                "when a.本期发生_借方 = 0 then '' \n" \
                "else \n" \
                "to_char(round(a.本期发生_借方, 2)) \n" \
                "end 本期发生_借方, \n" \
                "case \n" \
                "when instr(to_char(a.本期发生_贷方), '.') < 1 and a.本期发生_贷方 != 0 then a.本期发生_贷方 | | '.00' \n" \
                "when instr(to_char(a.本期发生_贷方), '.') + 1 = length(a.本期发生_贷方) and a.本期发生_贷方 != 0 then a.本期发生_贷方 | | '0' \n" \
                "when a.本期发生_贷方 = 0 then '' \n" \
                "else \n" \
                "to_char(round(a.本期发生_贷方, 2)) \n" \
                "end 本期发生_贷方, \n" \
                "case \n" \
                "when instr(to_char(a.累计发生_借方), '.') < 1 and a.累计发生_借方 != 0 then a.累计发生_借方 | | '.00' \n" \
                "when instr(to_char(a.累计发生_借方), '.') + 1 = length(a.累计发生_借方) and a.累计发生_借方 != 0 then a.累计发生_借方 | | '0' \n" \
                "when a.累计发生_借方 = 0 then '' \n" \
                "else \n" \
                "to_char(round(a.累计发生_借方, 2)) \n" \
                "end 累计发生_借方, \n" \
                "case \n" \
                "when instr(to_char(a.累计发生_贷方), '.') < 1 and a.累计发生_贷方 != 0 then a.累计发生_贷方 | | '.00' \n" \
                "when instr(to_char(a.累计发生_贷方), '.') + 1 = length(a.累计发生_贷方) and a.累计发生_贷方 != 0 then a.累计发生_贷方 | | '0' \n" \
                "when a.累计发生_贷方 = 0 then '' \n" \
                "else \n" \
                "to_char(round(a.累计发生_贷方, 2)) \n" \
                "end 累计发生_贷方, \n" \
                "(case \n" \
                "  when sum(期末余额_借方)-sum(期末余额_贷方) >0 then \n" \
                "    sum(期末余额_借方)-sum(期末余额_贷方) \n" \
                "end) 期末余额_借方, \n" \
                "(case \n" \
                "  when sum(期末余额_贷方)-sum(期末余额_借方) >0 then \n" \
                "    sum(期末余额_贷方)-sum(期末余额_借方) \n" \
                "end) 期末余额_贷方 \n" \
                " from  \n" \
                "( \n" \
                "select  \n" \
                "a.*, \n" \
                "sum(c.累计发生_借方) 累计发生_借方, sum(c.累计发生_贷方) 累计发生_贷方 \n" \
                " from \n" \
                "( \n" \
                "select  \n" \
                "a.\"年度\",a.\"单位代码\",a.\"单位名称\",a.\"账套代码\",a.\"账套名称\",a.\"科目代码\",a.\"科目名称\",a.期初余额_借方,a.期初余额_贷方, \n" \
                "sum(d.本期发生_借方) 本期发生_借方, \n" \
                "sum(d.本期发生_贷方) 本期发生_贷方 \n" \
                " from  \n" \
                "( \n" \
                "select \n" \
                "a.年度,a.单位代码,a.单位名称,a.账套代码,a.账套名称,a.科目代码,a.科目名称, \n" \
                "(case \n" \
                "  when sum(b.期初余额_借方)-sum(b.期初余额_贷方) >0 then \n" \
                "    sum(b.期初余额_借方)-sum(b.期初余额_贷方) \n" \
                "end) 期初余额_借方, \n" \
                "(case \n" \
                "  when sum(b.期初余额_贷方)-sum(b.期初余额_借方) >0 then \n" \
                "    sum(b.期初余额_贷方)-sum(b.期初余额_借方) \n" \
                "end) 期初余额_贷方 \n" \
                "from V_BASE_ALLUNIT_余额表_通用字段 a \n" \
                "left join V_BASE_ALLUNIT_期初余额 b on  b.年度=a.年度 and b.单位代码=a.单位代码 and b.账套代码=a.账套代码 and b.科目代码=a.科目代码 and b.会计期间 between 0 and " + month_start_qc + " \n" \
                "group by a.年度,a.单位代码,a.单位名称,a.账套代码,a.账套名称,a.科目代码,a.科目名称 \n" \
                "order by a.科目代码 \n" \
                ") a \n" \
                "left join V_BASE_ALLUNIT_本期发生 d on  d.年度=a.年度 and d.单位代码=a.单位代码 and d.账套代码=a.账套代码 and d.科目代码=a.科目代码 and d.会计期间 in(" + month_start + "," + month_end + ") \n" \
                "group by a.年度,a.单位代码,a.单位名称,a.账套代码,a.账套名称,a.科目代码,a.科目名称,a.期初余额_借方,a.期初余额_贷方 \n" \
                "order by a.科目代码 \n" \
                ") a \n" \
                "left join V_BASE_ALLUNIT_累计发生 c on  c.年度=a.年度 and c.单位代码=a.单位代码 and c.账套代码=a.账套代码 and c.科目代码=a.科目代码 and c.会计期间 between 1 and " + month_end + " \n" \
                "group by a.年度,a.单位代码,a.单位名称,a.账套代码,a.账套名称,a.科目代码,a.科目名称,a.期初余额_借方,a.期初余额_贷方,a.本期发生_借方,a.本期发生_贷方 \n" \
                "order by a.科目代码 \n" \
                ")a \n" \
                "left join V_BASE_ALLUNIT_期末余额 d on  d.年度=a.年度 and d.单位代码=a.单位代码 and d.账套代码=a.账套代码 and d.科目代码=a.科目代码 and d.会计期间 between 0 and " + month_end + " \n" \
                "group by a.年度,a.单位代码,a.单位名称,a.账套代码,a.账套名称,a.科目代码,a.科目名称,a.期初余额_借方,a.期初余额_贷方,a.本期发生_借方,a.本期发生_贷方,a.累计发生_借方,a.累计发生_贷方 \n" \
                "order by a.科目代码 \n" \
                ") \n" \
                "where 单位代码='" + dw + "' and 年度='" + nd + "' and 账套代码='" + zt + "'"
            print("sql 语句: 2")

        conn = cx_Oracle.connect("AIXED_20211111", "xzsijjcw", "10.1.67.12:1521/xzrszjk")
        cursor = conn.cursor()
        data = cursor.execute(sql)

        #data = db.session.execute(sql)
        rows = data.fetchall()

        cursor.execute('commit')
        cursor.close()

        print("总行数:", len(rows))

        result = []
        temp = {}

        for row in rows:
            temp = {
                'ND': row[0],
                'CO_CODE': row[1],
                'CO_NAME': row[2],
                'ACCOUNT_ID': row[3],
                'ACCOUNT_NAME': row[4],
                'ACC_CODE': row[5],
                'ACC_NAME': row[6],
                'QCYE_JF': row[7],
                'QCYE_DF': row[8],
                'BQFS_JF': row[9],
                'BQFS_DF': row[10],
                'LJFS_JF': row[11],
                'LJFS_DF': row[12],
                'QMYE_JF': row[13],
                'QMYE_DF': row[14],
            }

            # print("条目:", i, row[0], row[1], row[3], row[5])

            result.append(temp)
            temp = {}
        print(result)

        return jsonify(result)

    else:
        return jsonify("请求方式错误")


# 查询.用户权限职位表
@app.route('/api/InfoQuery/userrolezw', methods=['GET'])
def 信息查询_用户权限职位():
    if request.method == "GET":

        # 取所有类型  用这个 下面那个 报错
        nd = request.values.get('nd')
        dw = request.values.get("dw")
        zt = request.values.get("zt")
        uid = request.values.get("uid")

        print('[GET] 年度:', nd)
        print('[GET] 单位:', dw)
        print('[GET] 账套代码:', zt)
        print('[GET] 用户ID:', uid)

        # select 年度,单位编码,单位名称,用户名,用户ID,权限组,职位 from V_BASE_USER_用户状态职位账套 t

        if uid == '' or uid == None:
            sql = "select 年度,单位编码,单位名称,所属账套代码,所属账套名称,用户名,用户ID,权限组,职位 from V_BASE_USER_用户状态职位账套 t  " \
                  "where 年度 = " + "'" + nd + "'" + " and " + "单位编码=" + "'" + dw + "'" + " and " + "所属账套代码=" + "'" + zt + "'"

        else:
            sql = "select 年度,单位编码,单位名称,所属账套代码,所属账套名称,用户名,用户ID,权限组,职位 from V_BASE_USER_用户状态职位账套 t  " \
                  "where 年度 = " + "'" + nd + "'" + " and " + "单位编码=" + "'" + dw + "'" + " and " + "所属账套代码=" + "'" + zt + "'" + " and " + "用户ID=" + "'" + uid + "'"

        print("sql 语句:", sql)

        data = db.session.execute(sql)
        # db.session.commit()  select 不需要提交

        rows = data.fetchall()

        print("总行数:", len(rows))
        if len(rows) == 0:
            return jsonify("无数据")
        result = []
        temp = {}

        for row in rows:
            temp = {
                'ND': row[0],
                'CO_CODE': row[1],
                'CO_NAME': row[2],
                'ACCOUNT_CODE': row[3],
                'ACCOUNT_NAME': row[4],
                'USER_NAME': row[5],
                'USER_CODE': row[6],
                'ROLE_NAME': row[7],
                'ROLE_ZW': row[8],

            }

            # print("条目:", i, row[0], row[1], row[3], row[5])

            result.append(temp)
            temp = {}

        print("所有数据:", result)

        return jsonify(result)

    else:
        return jsonify("请求方式错误")

# 查询.出纳人员账簿表
@app.route('/api/InfoQuery/bankaccount', methods=['GET'])
def 信息查询_出纳人员账簿():
    if request.method == "GET":

        # 取所有类型  用这个 下面那个 报错
        nd = request.values.get('nd')
        dw = request.values.get("dw")
        zt = request.values.get("zt")
        uid = request.values.get("uid")

        print('[GET] 年度:', nd)
        print('[GET] 单位:', dw)
        print('[GET] 账套代码:', zt)
        print('[GET] 用户ID:', uid)

        # select 年度,单位编码,单位名称,用户名,用户ID,权限组,职位 from V_BASE_USER_用户状态职位账套 t


        sql = "select * from V_BASE_出纳账簿查询 t " \
            "where org_id like '%" + dw + "%' and accountset like '%" + zt + "%' and instr(year,'" + nd + "')>0 and user_id like '%" + uid + "%' order by user_id"

        print("sql 语句:", sql)

        data = db.session.execute(sql)
        # db.session.commit()  select 不需要提交

        rows = data.fetchall()

        print("总行数:", len(rows))
        if len(rows) == 0:
            return jsonify("无数据")
        result = []
        temp = {}

        for row in rows:
            temp = {
                'accountset': row[1],
                'accountcode': row[2],
                'accountbook': row[3],
                'org_id': row[4],
                'subject': row[7],
                'bank': row[8],
                'account_number': row[9],
                'address': row[10],
                'year': row[17],
                'USER_ID': row[36],
                'CO_NAME': row[37],
                'COA_NAME': row[38],
                'USER_NAME': row[39],
            }

            # print("条目:", i, row[0], row[1], row[3], row[5])

            result.append(temp)
            temp = {}

        print("所有数据:", result)

        return jsonify(result)

    else:
        return jsonify("请求方式错误")


# 查询.用户年度登陆情况表
@app.route('/api/InfoQuery/useryearuseinfo', methods=['GET'])
def 信息查询_用户年度登陆情况():
    if request.method == "GET":

        # 取所有类型  用这个 下面那个 报错
        nd = request.values.get('nd')
        uid = request.values.get("uid")

        print('[GET] 年度:', nd)
        print('[GET] 用户ID:', uid)

        if uid == '' or uid == None:
            sql = "select * from V_BASE_USER_LOGIN_YEAR t  " \
                  "where YEAR = " + "'" + nd + "'" + "order by ONLINE_TIME_MINUTE desc"
        else:
            sql = "select * from V_BASE_USER_LOGIN_YEAR t  " \
                  "where YEAR = " + "'" + nd + "'" + " and " + "USER_ID=" + "'" + uid + "'"

        print("sql 语句:", sql)

        data = db.session.execute(sql)
        rows = data.fetchall()

        print("总行数:", len(rows))
        if len(rows) == 0:
            return jsonify("无数据")
        result = []
        temp = {}

        for row in rows:
            temp = {
                'ND': row[0],
                'USER_ID': row[1],
                'LASTLOGIN_IP': row[2],
                'LASTLOGIN_TIME': row[3],
                'LASTLOGINOUT_TIME': row[4],
                'ONLINE_TIME_MINUTE': row[5],
                'LOGIN_INC': row[6],

            }

            # print("条目:", i, row[0], row[1], row[3], row[5])

            result.append(temp)
            temp = {}

        print("所有数据:", result)

        return jsonify(result)

    else:
        return jsonify("请求方式错误")


# 查询.用户总共登陆情况表
@app.route('/api/InfoQuery/useralluseinfo', methods=['GET'])
def 信息查询_用户总共登陆情况():
    if request.method == "GET":

        # 取所有类型  用这个 下面那个 报错
        uid = request.values.get("uid")

        print('[GET] 用户ID:', uid)

        if uid == '' or uid == None:
            sql = "select * from V_BASE_USER_LOGIN_ONLY t order by 登陆频次 desc  "
        else:
            sql = "select * from V_BASE_USER_LOGIN_ONLY t " \
                  "where USER_ID = " + "'" + uid + "'"

        print("sql 语句:", sql)

        data = db.session.execute(sql)
        rows = data.fetchall()

        print("总行数:", len(rows))
        if len(rows) == 0:
            return jsonify("无数据")
        result = []
        temp = {}

        for row in rows:
            temp = {
                'USER_ID': row[0],
                'LASTLOGIN_IP': row[1],
                'LASTLOGIN_TIME': row[2],
                'LASTLOGINOUT_TIME': row[3],
                'LOGIN_INC': row[4],

            }

            # print("条目:", i, row[0], row[1], row[3], row[5])

            result.append(temp)
            temp = {}

        print("所有数据:", result)

        return jsonify(result)

    else:
        return jsonify("请求方式错误")


# 登帐情况表 按月
@app.route("/api/InfoQuery/dzqbk_ay", methods=['GET'])
def 信息查询_登帐情况表_按月():
    if request.method == 'GET':

        # 取所有类型  用这个 下面那个 报错
        nd = request.values.get('nd')
        dw = request.values.get("dw")
        zt = request.values.get("zt")

        print('[GET] 年度:', nd)
        print('[GET] 单位:', dw)
        print('[GET] 账套:', zt)

        if zt == '' or zt == None:
            sql = "select * from V_BASE_会计登账情况表_按月分类 t " \
                  "where 年度 = " + "'" + nd + "'" + " and " + "单位代码=" + "'" + dw + "'"
        else:
            sql = "select * from V_BASE_会计登账情况表_按月分类 t " \
                  "where 年度 = " + "'" + nd + "'" + " and " + "单位代码=" + "'" + dw + "'" + " and " + "账套代码=" + "'" + zt + "'"

        print("sql 语句:", sql)

        data = db.session.execute(sql)
        # db.session.commit()  select 不需要提交

        rows = data.fetchall()

        print("总行数:", len(rows))
        if len(rows) == 0:
            return jsonify("无数据")
        i = 1
        temp = {}
        result = []
        for row in rows:
            temp["ND"] = row[0]
            temp["KJQJ"] = row[1]
            temp["DWDM"] = row[2]
            temp["DWMC"] = row[3]
            temp["ZTDM"] = row[4]
            temp["ZTMC"] = row[5]
            temp["PZZS"] = row[6]

            # print("row:", i, row[0], row[1], row[2], row[3])
            i = i + 1
            result.append(temp.copy())

        return jsonify(result)

    else:
        return jsonify("请求方式错误")


# 登帐情况表 按人
@app.route("/api/InfoQuery/dzqbk_ar", methods=['GET'])
def 信息查询_登帐情况表_按人():
    if request.method == 'GET':

        # 取所有类型  用这个 下面那个 报错
        nd = request.values.get('nd')
        dw = request.values.get("dw")
        zt = request.values.get("zt")
        zdr = request.values.get("zdr")

        print('[GET] 年度:', nd)
        print('[GET] 单位:', dw)
        print('[GET] 账套:', zt)
        print('[GET] 制单人:', zdr)

        if zt == '':
            if zdr == '':
                sql = "select * from V_BASE_会计登账情况表_按人分类 t " \
                      "where 年度 = " + "'" + nd + "'" \
                      + " and " + "单位代码=" + "'" + dw + "'"
            else:
                sql = "select * from V_BASE_会计登账情况表_按人分类 t " \
                      "where 年度 = " + "'" + nd + "'" \
                      + " and " + "单位代码=" + "'" + dw + "'" \
                      + " and " + "制单人=" + "'" + zdr + "'"

        elif zdr == '':

            sql = "select * from V_BASE_会计登账情况表_按人分类 t " \
                  "where 年度 = " + "'" + nd + "'" + " and " + "单位代码=" + "'" + dw + "'" + " and " + "账套代码=" + "'" + zt + "'"

        else:

            sql = "select * from V_BASE_会计登账情况表_按人分类 t " \
                  "where 年度 = " + "'" + nd + "'" \
                  + " and " + "单位代码=" + "'" + dw + "'" \
                  + " and " + "账套代码=" + "'" + zt + "'" \
                  + " and " + "制单人=" + "'" + zdr + "'"

        print("sql 语句:", sql)

        data = db.session.execute(sql)
        # db.session.commit()  select 不需要提交

        rows = data.fetchall()

        print("总行数:", len(rows))
        if len(rows) == 0:
            return jsonify("无数据")
        i = 1
        temp = {}
        result = []
        for row in rows:
            temp["ND"] = row[0]
            temp["DWDM"] = row[1]
            temp["DWMC"] = row[2]
            temp["ZTDM"] = row[3]
            temp["ZTMC"] = row[4]
            temp["ZDR"] = row[5]
            temp["ZDRXM"] = row[6]
            temp["PZJZZT"] = row[7]
            temp["ZPZS"] = row[8]

            # print("row:", i, row[0], row[1], row[2], row[3])
            i = i + 1
            result.append(temp.copy())

        return jsonify(result)

    else:
        return jsonify("请求方式错误")


# 登帐情况表 按账套
@app.route("/api/InfoQuery/dzqbk_ztfl", methods=['GET'])
def 信息查询_登帐情况表_账套分类():
    if request.method == 'GET':

        # 取所有类型  用这个 下面那个 报错
        nd = request.values.get('nd')
        dw = request.values.get("dw")
        zt = request.values.get("zt")

        print('[GET] 年度:', nd)
        print('[GET] 单位:', dw)
        print('[GET] 账套:', zt)

        # 参数检查
        if nd == None or dw == None:
            return '参数错误'

        if zt == '' or zt == None:
            sql = "select * from V_BASE_会计登账情况表_账套分类 t " \
                  "where 年度 = " + "'" + nd + "'" + " and " + "单位代码=" + "'" + dw + "'"
        else:
            sql = "select * from V_BASE_会计登账情况表_账套分类 t " \
                  "where 年度 = " + "'" + nd + "'" + " and " + "单位代码=" + "'" + dw + "'" + " and " + "账套代码=" + "'" + zt + "'"

        print("sql 语句:", sql)

        data = db.session.execute(sql)
        # db.session.commit()  select 不需要提交

        rows = data.fetchall()

        print("总行数:", len(rows))
        if len(rows) == 0:
            return jsonify("无数据")
        i = 1
        temp = {}
        result = []
        for row in rows:
            temp["ND"] = row[0]
            temp["DWDM"] = row[1]
            temp["DWMC"] = row[2]
            temp["ZTDM"] = row[3]
            temp["ZTMC"] = row[4]
            temp["PZZS"] = row[5]

            # print("row:", i, row[0], row[1], row[2], row[3])
            i = i + 1
            result.append(temp.copy())

        return jsonify(result)

    else:
        return jsonify("请求方式错误")


# 查询 凭证编号
@app.route("/api/InfoQuery/pzbh", methods=['GET'])
def 信息查询_凭证编号():
    if request.method == 'GET':

        # 取所有类型  用这个 下面那个 报错
        nd = request.values.get('nd')
        yf = request.values.get("yf")
        zt = request.values.get("zt")
        dw = request.values.get("dw")

        print('[GET] 年度:', nd)
        print('[GET] 月份:', yf)
        print('[GET] 账套:', zt)
        print('[GET] 单位:', dw)


        if yf == '00':

            sql = "select * from V_BASE_USER_PZBH_UNIT t " \
                  "where nd = " + "'" + nd + "'" + " and " + "co_code like " + "'%" + dw + "%'" + " and " + "account_id like " + "'%" + zt + "%'" + " order by month"

        else:
            sql = "select * from V_BASE_USER_PZBH_UNIT t " \
                  "where nd = " + "'" + nd + "'" + " and " + "co_code like " + "'%" + dw + "%'" + " and " + "account_id like " + "'%" + zt + "%'" + " and " + "month = " + "'" + yf + "'" + " order by month"

        print('[SQL]', sql)



        try:
            data = db.session.execute(sql)
            rows = data.fetchall()
        except Exception as msg:
            print('[查询凭证] 执行异常', msg)
            return '操作成功!'
        finally:
            pass

        print("总行数:", len(rows))
        if len(rows) == 0:
            return jsonify("无数据")

        temp = {}

        result = []

        result_ = {}

        for row in rows:
            temp["ND"] = row[0]
            temp["CO_CODE"] = row[1]
            temp["CO_NAME"] = row[2]
            temp["ACCOUNT_ID"] = row[3]
            temp["MOUTH"] = row[4]
            temp["CUR_INDEX"] = row[5]

            month_ = row[4]
            month_end = month_[0].strip('0') + month_[1:]

            sql_detail = "select vou_no,vou_date,vou_desc,amt_cr,vou_source,print_status,inputor,acce_cnt,amt_dr,auditor,poster,adate,post_date,status,compo_source,modifytime,fileader,CDATE " \
                 "from GL_VOU_HEAD t " \
                 "where co_code='" + row[1] + "' and account_id like '%" + row[3] + "%' and fiscal like '%" + row[0] + "%' and fis_perd = '" + month_end + "'"

            print('[SQL明细]', sql_detail)

            data_detail = db.session.execute(sql_detail)
            rows_detail = data_detail.fetchall()

            print("明细总行数:", len(rows_detail))

            temp_detail = {}
            result_detail = []
            for row_detail in rows_detail:
                # 凭证编号
                temp_detail["VOU_NO"] = row_detail[0]

                # 凭证日期
                temp_detail["VOU_DATE"] = str(row_detail[1])[0:10]

                # 凭证摘要
                temp_detail["VOU_DESC"] = row_detail[2]

                # 贷方金额
                temp_detail["AMT_CR"] = row_detail[3]

                # 凭证来源
                temp_detail["VOU_SOURCE"] = row_detail[4]

                # 打印状态
                temp_detail["PRINT_STATUS"] = row_detail[5]

                #录入人
                temp_detail["INPUTOR"] = row_detail[6]

                # 附件张数
                temp_detail["acce_cnt"] = row_detail[7]

                #借方金额
                temp_detail["amt_dr"] = row_detail[8]

                # 审核人
                temp_detail["auditor"] = row_detail[9]

                # 记账人
                temp_detail["poster"] = row_detail[10]

                # 审核日期
                temp_detail["adate"] = str(row_detail[11])[0:10]

                # 记账日期
                temp_detail["post_date"] = str(row_detail[12])[0:10]

                # 凭证状态
                temp_detail["status"] = row_detail[13]

                # 修改日期
                temp_detail["modifytime"] = str(row_detail[15])

                # 会计主管
                temp_detail["fileader"] = row_detail[16]

                # 创建日期
                temp_detail["CDATE"] = str(row_detail[17])[0:10]


                # print("row:", i, row[0], row[1], row[2], row[3])

                result_detail.append(temp_detail.copy())

            temp["detail"] = result_detail
            result.append(temp.copy())

            result_['base'] = result

        return jsonify(result_)


    else:
        return jsonify("请求方式错误")


# 修改 凭证编号
@app.route('/api/Edit/xgpzbh', methods=["POST"])
def 修改凭证编号():
    if request.method == 'POST':

        # 取所有类型  用这个 下面那个 报错
        nd = request.values.get('nd')
        co_code = request.values.get("co_code")
        account_id = request.values.get("account_id")
        month = request.values.get("month")

        if nd == None or co_code == None or account_id == None or month == None:
            # json 格式的数据
            reqParm = json.loads(request.data.decode())
            nd = reqParm['nd']
            co_code = reqParm['co_code']
            account_id = reqParm['account_id']
            month = reqParm['month']

            print('[收到Json格式数据]', 'nd', nd, 'co_code', co_code, 'account_id', account_id, 'month', month)

        print('[POST] 年度:', nd)
        print('[POST] 单位代码:', co_code)
        print('[POST] 账套代码:', account_id)
        print('[POST] 月份:', month)

        sql = "select CUR_INDEX from as_no t where fix_segs like \'" + co_code + nd + account_id + "%" + month + "\'"
        data = db.session.execute(sql)

        rows = data.fetchone()
        print(sql, '获取完成：数据条目', rows, '第一条数据：', rows[0])

        return jsonify(rows[0])

    else:
        return jsonify("请求方式错误")


if __name__ == '__main__':
    # 下面这行是支持中文的 不加的话中文就会乱码
    app.config['JSON_AS_ASCII'] = False

    # 支持跨域访问
    CORS(app, supports_credentials=True)

    app.run(host='0.0.0.0', port=5209, debug=True)
