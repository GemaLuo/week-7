from flask import Flask
from flask import request, jsonify, json
from flask import render_template
from flask import redirect
from flask import session
from flask_cors import CORS
from flask import url_for

#與資料庫連線
import mysql.connector 
website=mysql.connector.connect(
    host="localhost",
    user="root",
    password="0202", 
    db="website"
)
cursor=website.cursor() #獲得操作cursor游標:進行單行紀錄資料處理

app=Flask(
    __name__,
    static_folder="static",
    static_url_path="/"
)
CORS(app)
app.secret_key="test"

#首頁
@app.route("/")
def index():
    return render_template("index.html")

#註冊帳號
@app.route("/signup", methods=["POST"])
def signup():
    signname=request.form["signname"]
    username=request.form["username"]
    password=request.form["password"]
    sql="INSERT INTO member(name, username, password) VALUES(%s, %s, %s)" # %s – the argument is treated as and presented as a string
    val=signname, username, password #turn string into numberVal(S,V,Code) 
    cursor=website.cursor() #使用cursor方法
    cursor.execute("SELECT * FROM member WHERE username=%s",(username,))
    data_name=cursor.fetchone() #獲取一個數據
    if data_name is not None:
        return render_template("error.html", message="帳號已經被註冊")
    else:
        cursor.execute(sql, val) #執行mysql語句
        website.commit() #提交當前事務
        return render_template("index.html")
    

#登入：使用POST方法
@app.route("/signin", methods=["POST"])
def signin():
    username=request.form["username"]
    password=request.form["password"]
    if username=="" or password=="":
        return redirect ("http://127.0.0.1:3000/error?message=帳號或密碼輸入錯誤")
    data="SELECT * FROM member WHERE username=%s AND password=%s" # %string formatting 
    input= (username, password)
    cursor.execute(data, input) 
    result=cursor.fetchone()
    if result!=None: #若result正確
        session["signname"]=result[1]
        session["username"]=username
        session["password"]=password
        return render_template("member.html", signname=session['signname'])
    else:
        return redirect ("http://127.0.0.1:3000/error?message=帳號或密碼輸入錯誤")
    


#進入會員頁
@app.route("/member")
def member():
    if "signname" in session: #驗證成功，進入會員頁
        return render_template("member.html")
    else:
        return redirect("/")


#登出會員頁面，回到首頁
#登出時刪除紀錄
@app.route("/signout")
def signout():
    session.pop("signname", None) #刪除session
    return render_template("index.html")

#失敗頁面
@app.route("/error")
def error():
    message=request.args.get("message")
    return render_template("error.html", message=message)

#查詢會員資料
@app.route("/api/member", methods=["GET", "PATCH"])
def api():
    if request.method=="GET":
        username=request.args.get("username")
        cursor.execute("SELECT * FROM member WHERE username = %s",(username,))
        result=cursor.fetchone()
        if result is not None and "signname" in session:
            dict={
                "data":{
                    "id":result[0],
                    "name":result[1],
                    "username":result[2]
                }
            }
            return jsonify(dict)
        else:
            return {"data":None}
#更新會員資料
    if request.method=="PATCH":
        if "signname" in session:
            name=session["name"]
            rename=request.get_json()
            rename=rename["name"]
            sql="UPDATE member SET name= %s WHERE name= %s"
            val=(rename,name)
            cursor.execute(sql,val)
            website.commit()
            session["name"]=rename
            return {"ok": True}
        else:
            return{"error": True}

if __name__ == "__main__":
    app.run(debug=True, port=3000)