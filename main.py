from flask import Flask, flash, request, redirect, url_for, render_template
import mysql.connector as c
import urllib.request
import os
from werkzeug.utils import secure_filename

app = Flask(__name__)

user = list()

UPLOAD_FOLDER = 'static/images/product/'

app.secret_key = "secret key"
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024

ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg', 'gif'])

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def check_login():
    global user
    if len(user) == 1:

        return True
    else:
        return False

def check_admin_login():
    global user
    if len(user) == 1 and user[0][0] == 'admin':
        return True
    else:
        return False

def user_data():
    db = c.connect(host="localhost", user="root", password="12345", database="ecommerce_project")
    if db.is_connected():
        print(True)
    cursor = db.cursor();
    cursor.execute("Select * from user")
    users = cursor.fetchall()
    for i in users:
        print(i)
    return users

def product_data():
    db = c.connect(host="localhost", user="root", password="12345", database="ecommerce_project")
    if db.is_connected():
        print(True)
    cursor = db.cursor();
    cursor.execute("Select * from product")
    products = cursor.fetchall()
    for i in products:
        print(i)
    return products

@app.route('/')
@app.route("/home")
def index():
    global user
    username = None
    try:
        username = user[0][0]
    except Exception as e:
        pass

    db = c.connect(host="localhost", user="root", password="12345", database="ecommerce_project")
    if db.is_connected():
        print(True)
    cursor = db.cursor();
    cursor.execute("Select * from product where p_category='Hardware' limit 10")
    hardware_products = cursor.fetchall()
    print(hardware_products)

    cursor = db.cursor();
    cursor.execute("Select * from product where p_category='Software' limit 10")
    software_products = cursor.fetchall()
    print(software_products)
    return render_template("home.html", username=username, hardware_products=hardware_products, software_products=software_products)


@app.route('/product_hardware')
def product_hardware():
    global user
    username = None
    try:
        username = user[0][0]
    except Exception as e:
        pass

    db = c.connect(host="localhost", user="root", password="12345", database="ecommerce_project")
    if db.is_connected():
        print(True)
    cursor = db.cursor();
    cursor.execute("Select * from product where p_category='Hardware'")
    hardware_products = cursor.fetchall()
    print(hardware_products)
    return render_template("product_hardware.html", username=username, hardware_products=hardware_products)

@app.route('/product_software')
def product_software():
    global user
    username = None
    try:
        username = user[0][0]
    except Exception as e:
        pass

    db = c.connect(host="localhost", user="root", password="12345", database="ecommerce_project")
    if db.is_connected():
        print(True)
    cursor = db.cursor();
    cursor.execute("Select * from product where p_category='Software'")
    software_products = cursor.fetchall()
    print(software_products)
    return render_template("product_software.html", username=username, software_products=software_products)


@app.route("/login", methods=['POST','GET'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        print(email, password)

        db = c.connect(host="localhost", user="root", password="12345", database="ecommerce_project")
        if db.is_connected():
            print(True)
        cursor = db.cursor();

        cursor.execute("Select * from user where email='{}' and password='{}'".format(email, password))
        global user
        user = cursor.fetchall()
        print(user)
        print(type(user))
        if len(user)==1:
            print("Longin successfully")
            return redirect("/home")
        else:
            return redirect("login.html")

    return render_template("login.html")

@app.route("/logout")
def logout():
    global user
    if len(user) == 1:
        user.pop()
    return redirect('/home')

@app.route("/admin")
def admin():
    global user
    username = None
    try:
        username = user[0][0]
    except Exception as e:
        pass
    if check_admin_login():
        return render_template("admin.html", username=username)
    return redirect("/login")

@app.route("/signup")
def signup():
    return render_template("signup.html")

@app.route("/product_data/")
def product_data():
    global user
    username = None
    try:
        username = user[0][0]
    except Exception as e:
        pass

    if check_admin_login():
        #product = product_data()
        db = c.connect(host="localhost", user="root", password="12345", database="ecommerce_project")
        if db.is_connected():
            print(True)
        cursor = db.cursor();
        cursor.execute("Select * from product")
        products = cursor.fetchall()
        for i in products:
            print(i)
        return render_template("product_data.html", products=products, username=username)
    return redirect("/login")

@app.route("/product_data/product_add",methods=['POST', 'GET'])
def product_add():


    if (request.method == "POST"):
        data = request.form.to_dict()
        print(data)
        f = request.files['image']
        #f.save()
        filename = data['productid']+'.'+secure_filename(f.filename.split(".")[-1])

        f.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

        print(data)
        db = c.connect(host="localhost", user="root", password="12345", database="ecommerce_project")
        if db.is_connected():
            print(True)

        cursor = db.cursor()

        cursor.execute("insert into product values ('{}','{}','{}', '{}','{}','{}','{}');".format(data['productid'],
                                                                                           data['product_name'],
                                                                                           data['price'],
                                                                                           data['detail'],
                                                                                           data['category'],
                                                                                           data['company_id'],
                                                                                           str(os.path.join(app.config['UPLOAD_FOLDER'])+filename)))
        db.commit()

    db = c.connect(host="localhost", user="root", password="12345", database="ecommerce_project")
    if db.is_connected():
        print(True)
    cursor = db.cursor();
    cursor.execute("Select * from product")
    products = cursor.fetchall()
    return render_template("product_data.html",products = products)

@app.route("/user_data")
def user_data():
    global user
    username = None
    try:
        username = user[0][0]
    except Exception as e:
        pass
    if check_admin_login():
        db = c.connect(host="localhost", user="root", password="12345", database="ecommerce_project")
        if db.is_connected():
            print(True)
        cursor = db.cursor();
        cursor.execute("Select * from user")
        users = cursor.fetchall()
        for i in users:
            print(i)
        #users = user_data()
        return render_template("user_data.html", username=username, users=users)
    return redirect("/login")

@app.route("/thankyou", methods=['POST','GET'])
def thankyou():
    if request.method == 'POST':
        data = request.form.to_dict()

        print(data)

        db = c.connect(host="localhost", user="root", password="12345", database="ecommerce_project")

        cursor = db.cursor()

        cursor.execute("insert into user values ('{}','{}','{}', '{}','{}');".format(data['username'],data['name'], data['address'], data['email'], data['password']))
        db.commit()
        return render_template("thankyou.html", name=data['username'])

if __name__ == '__main__':
    app.run(debug=True)

# See PyCharm help at https://www.jetbrains.com/help/pycharm/
