#coding=utf-8
from  flask import Flask,request,jsonify,make_response,abort
from flask_cors import *
import pymysql,json,xlrd
from datetime import datetime

app=Flask(__name__)
CORS(app, supports_credentials=True)
config ={
        'host':'192.168.20.155',
        'port':3306,
        'user':'test',
        'passwd':'test123',
        'db':'cts',
        'charset':'utf8',
        }

save_path='D:\\'
ALLOWED_EXTENSIONS = set(['xls', 'xlsx'])
def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS

@app.route('/import_excel', methods=[ 'POST'])
def import_device():
    file = request.files['files[]']
    filename = file.filename
    # 判断文件名是否合规
    if file and allowed_file(filename):
        file.save(save_path+filename)
        excelName = save_path+filename
        bk = xlrd.open_workbook(excelName, encoding_override="utf-8")
        sh = bk.sheets()[0]  # 因为Excel里只有sheet1有数据，如果都有可以使用注释掉的语句
        ncols = sh.ncols#列

        conn = pymysql.connect(**config)
        cur = conn.cursor()
        for j in range(ncols+1):
            if j > ncols:
                return jsonify({'msg': "ok", "remark": "上传成功"})
            else:
                try:
                    lvalues = sh.row_values(j+1)
                    cur.execute('insert into mock_config values (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)',(None,lvalues[0],lvalues[4],lvalues[3],lvalues[2],lvalues[6],lvalues[5],datetime.now(),0,lvalues[1]))
                    conn.commit()
                except:
                    return jsonify({'msg': "fail", "remark": "解析失败"})
        conn.close()
        return jsonify({'msg': "ok", "remark": "上传成功"})
    else:
        return jsonify({'msg': "fail", "remark": "上传文件不符合格式要求"})

@app.route('/addinfo',methods=['POST'])
def  query_user():
    title=request.form['title']
    method=request.form['method']
    reqparams=request.form['reqparams']
    resparams=request.form['resparams']
    des=request.form['des']
    domain=request.form['domain']
    project_name=request.form['projectName']
    if not request.json or not 'title' in request.json:
        abort(400)
    if title == '':
        return jsonify({'msg': "fail", "remark": "title不能为空"})
    try:
        conn = pymysql.connect(**config)
        cur = conn.cursor()
        cur.execute('insert into mock_config (title,reqparams,methods,domain,description,resparams,status,project_name) '
                    'values (%s,%s,%s,%s,%s,%s,%s,%s) ',(title,reqparams,method,domain,des,resparams,0,project_name))
        conn.commit()
        conn.close()
    except :
        return jsonify({'msg': "fail", "remark": "save data fail"})
    return jsonify({'msg': "ok","remark":""})

@app.route('/delinfo',methods=['POST'])
def  delinfo():
    id=request.form.getlist('id[]')
    conn = pymysql.connect(**config)
    cur = conn.cursor()
    try:
        for index in range(len(id)):
            idd=id[index]
            cur.execute('delete from mock_config where id=%s',(idd))
        conn.commit()
        conn.close()
    except :
        return jsonify({'msg': "fail", "remark": "delete fail"})
    return jsonify({'msg': "ok","remark":""})

@app.route('/editinfo',methods=['POST'])
def  editinfo():
    title = request.form['title']
    method = request.form['method']
    reqparams = request.form['reqparams']
    resparams = request.form['resparams']
    des = request.form['reqparams']
    domain = request.form['domain']
    id=request.form['id']
    project_name=request.form['projectName']
    conn = pymysql.connect(**config)
    cur = conn.cursor()
    try:
        cur.execute('update mock_config set title=%s,reqparams=%s,methods=%s,domain=%s,description=%s,resparams=%s,update_time=%s,project_name=%s where id=%s',(title, reqparams, method, domain, des, resparams,datetime.now().strftime('%y-%m-%d %H:%M:%S'),project_name,id))
        conn.commit()
        conn.close()
    except:
        return jsonify({'msg': "fail", "remark": "save data fail"})
    return jsonify({'msg': "ok", "remark": ""})

@app.route('/selectinfo',methods=['GET'])
def  selectinfo():
    id=request.args.get("id")
    conn = pymysql.connect(**config)
    cur = conn.cursor()
    try:
        cur.execute('select title,reqparams,methods,domain,description,resparams,project_name from mock_config where id=%s',(id))
        re= cur.fetchall()
        conn.close()
        key = ('title', 'reqparams', 'methods', 'domain', 'description', 'resparams','project_name')
        d = [dict(zip(key, value)) for value in re]
    except:
        return jsonify({'msg': "fail", "remark": "select data fail"})
    return jsonify({'msg': "ok", "remark": "", 'data':d})

@app.route('/manage',methods=['POST'])
def  manage():
    id = request.form['id']
    status = request.form['status']
    conn = pymysql.connect(**config)
    cur = conn.cursor()
    try:
        cur.execute('update mock_config set status=%s where id=%s',(status,id))
        conn.commit()
        conn.close()
    except:
        return jsonify({'msg': "fail", "remark": "select data fail"})
    return jsonify({'msg': "ok", "remark": ""})

@app.route('/search',methods=['GET'])
def  search():
    title=request.args.get("title").strip()
    project_name = request.args.get("project_name")
    if title is not None and project_name == str(0):
        sql = "select id,status,title,reqparams,methods,domain,description,resparams,date_format(update_time,'%Y-%m-%d %H:%i:%s') from mock_config where title like '%" + title + "%'"
    elif title is not None and project_name is not None:
        sql = "select id,status,title,reqparams,methods,domain,description,resparams,date_format(update_time,'%Y-%m-%d %H:%i:%s') from mock_config where project_name='" + project_name + "' and title like '%" + title + "%'"
    else:
        sql = "select id,status,title,reqparams,methods,domain,description,resparams,date_format(update_time,'%Y-%m-%d %H:%i:%s') from mock_config where project_name='" + project_name+"'"
    try:
        conn = pymysql.connect(**config)
        cur = conn.cursor()
        cur.execute(sql)
        re= cur.fetchall()
        conn.close()
        key = ('id','status','title', 'reqparams', 'methods', 'domain', 'description', 'resparams','updateTime')
        d = [dict(zip(key, value)) for value in re]
    except:
        return jsonify({'msg': "fail", "remark": "select data fail"})
    return jsonify({'msg': "ok", "remark": "", "data": d})

@app.route('/searchall',methods=['GET'])
def  searchall():
    conn = pymysql.connect(**config)
    cur = conn.cursor()
    try:
        cur.execute("select id,title,reqparams,methods,domain,description,resparams,status,date_format(update_time,'%Y-%m-%d %H:%i:%s') from mock_config")
        re= cur.fetchall()
        conn.close()
        key = ('id','title', 'reqparams', 'methods', 'domain', 'description', 'resparams','status','updateTime')
        d = [dict(zip(key, value)) for value in re]
    except:
        return jsonify({'msg': "fail", "remark": "select data fail"})
    return jsonify({'msg': "ok", "remark": "","data": d})

@app.route('/searchproject',methods=['GET'])
def  searchproject():
    conn = pymysql.connect(**config)
    cur = conn.cursor()
    try:
        cur.execute("SELECT DISTINCT(project_name) from mock_config")
        re= cur.fetchall()
        conn.close()
    except:
        return jsonify({'msg': "fail", "remark": "select data fail"})
    return jsonify({'msg': "ok", "remark": "","data": re})

@app.errorhandler(404)
def not_found(error):
    return make_response(jsonify({'msg':'fail','error': '404 Not found'}), 404)

@app.errorhandler(500)
def not_found(error):
    return make_response("程序报错，可能是因为叙利亚战争导致", 500)

if __name__=="__main__":
    app.run(host='0.0.0.0',debug=True,threaded=True,port=5202)

