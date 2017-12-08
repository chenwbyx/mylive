from flask import Flask,render_template,url_for,session,request,g,redirect,jsonify,Response
from flask_sqlalchemy import SQLAlchemy
from models import Mydata
from exts import db
import json,urllib,operator,pymysql,config,os
from werkzeug.utils import secure_filename
from sqlalchemy import or_,func

#允许的文件类型
ALLOWED_EXTENSIONS = set([ 'png', 'jpg', 'jpeg', 'gif'])

app = Flask(__name__)
app.config.from_object(config)
db = SQLAlchemy(app)
pymysql.install_as_MySQLdb()


def Mydata_json(obj):
    return{
        "id":obj.id,
        "content":obj.content,
        "create_time":obj.create_time,
        "photo_path":obj.photo_path,
        "flag":obj.flag
    }

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS


@app.route('/admin/')
def admin():
    if session.get('username') != 'admin':
        return render_template('login.html')
    else:
        cont = {
            'Mydata': Mydata.query.all(),
            'n_Mydata': db.session.query(func.count('*')).select_from(Mydata).scalar(), #获取行数
            'flag_addfile':request.args.get("flag_addfile"),
            'flag_deletefile':request.args.get("flag_deletefile"),
            'flag_revisesucceed':request.args.get('flag_revisesucceed'),
            'flag_photofile':request.args.get('flag_photofile')
        }
        if request.args.get("flag_revisefile"):
            mydata_tmp=Mydata.query.get(request.args.get("flag_revisefile"))
        else:
            mydata_tmp='NULL'
        cmpfun = operator.attrgetter('id')  # 自定义排序规则
        cont['Mydata'].sort(key=cmpfun, reverse=True)
        return render_template('admin.html', **cont,mydata_tmp=mydata_tmp)

@app.route('/add/', methods=['GET', 'POST'])
def add():
    if request.method == 'GET':
        if session.get('username') != 'admin':
            return render_template('login.html')
        else:
            return render_template('admin.html')
    else:
        f = request.files['file']
        cont=request.form['content']
        if f:
            if allowed_file(f.filename):
                basepath = os.path.dirname(__file__)  # 当前文件所在路径
                upload_path = os.path.join(basepath, 'static/images',secure_filename(f.filename))      #  注意：没有的文件夹一定要先创建，不然会提示没有该路径
                f.save(upload_path)
            else:
                render_template('admin.html', flag_photofile=1)
        if request.form['revise_flag']!='0':
            mydata_tmp = Mydata.query.get(request.form['revise_flag'])
            mydata_tmp.content = cont;
            mydata_tmp.photo_path = f.filename
            db.session.commit();
            print('修改')
            return redirect(url_for('admin',flag_revisesucceed=1))
        else:
            mydata_tmp=Mydata(content=cont,photo_path=f.filename,flag=int(request.form['sub_flag']))
            db.session.add(mydata_tmp)
            db.session.commit()
            print('添加')
            return redirect(url_for('admin',flag_addfile=1))

@app.route('/revise/',methods=['GET','POST'])
def revise():
    if request.method=='GET':
        if session.get('username')!='admin':
            return render_template('login.html')
        else:
            mydata1=Mydata.query.get(request.args.get("id"))
            return redirect(url_for('admin',flag_revisefile=request.args.get("id")))
    else:
        pass
        # f = request.files['file']
        # cont=request.form['content']
        # if request.form['sub_flag']=='yes':
        #     flag=1
        # else:
        #     flag=0
        # if f and allowed_file(f.filename):
        #     basepath = os.path.dirname(__file__)  # 当前文件所在路径
        #     upload_path = os.path.join(basepath, 'static\images',secure_filename(f.filename))  # 注意：没有的文件夹一定要先创建，不然会提示没有该路径
        #     f.save(upload_path)
        # else:
        #     return u'请上传合法文件！！！'
        # mydata1 = Mydata.query.get(request.args.get("id"))
        # mydata1.content=cont;
        # mydata1.photo_path=f.filename
        # db.session.commit();
        # return render_template('admin.html', flag_revisefile=1)


@app.route('/delete/',methods=['GET','POST'])
def delete():
    if request.method=='GET':
        if session.get('username')!='admin':
            return render_template('login.html')
        else:
            from models import db
            mydata1=Mydata.query.get(request.args.get("id"))
            db.session.delete(mydata1)
            db.session.commit()
            return redirect(url_for('admin',flag_deletefile=1))
    else:
        pass

@app.route('/login/',methods=['GET','POST'])
def login():
    if request.method=='GET':
        return render_template('login.html')
    else:
        if request.form['username']=='admin'and request.form['password']=='dropsxyz':
            session['username']='admin'
            return redirect(url_for('admin'))
        else:
            return render_template('login.html',flag_loginfail=1)

@app.route('/logout/')
def logout():
    session.pop('username')
    return render_template('login.html')

@app.route('/',methods=['Get'])
def hello_world():
    if session.get('username') == 'admin':
        isadmin=1
    else:
        isadmin=0
    cont={
        'Mydata':Mydata.query.all(),
        'n_Mydata':db.session.query(func.count('*')).select_from(Mydata).scalar(),
    }
    cmpfun=operator.attrgetter('id')#自定义排序规则
    cont['Mydata'].sort(key=cmpfun,reverse=True)
    return render_template('index.html',**cont)

# @app.route('/updata/')
# def updata():
#     if session.get('username') == 'admin':
#         isadmin=1
#     else:
#         isadmin=0
#     cont = {
#         'Mydata': Mydata.query.all(),
#         'n_Mydata': db.session.query(func.count('*')).select_from(Mydata).scalar(),  # 获取行数
#         'isadmin': isadmin
#     }
#     # cont=cont.__dict__
#     # cont=json.dumps(cont)
#     print(type(cont))
#     return json.dumps(cont['Mydata'],default=lambda o:o.__repr__())
#     #return json.dumps(cont['Mydata'],default=lambda obj:obj.__dict__,sort_keys=True,indent=4)


if __name__ == '__main__':
    app.run(port=8080,host='0.0.0.0')
