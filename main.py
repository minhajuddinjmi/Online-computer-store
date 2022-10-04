from flask import Flask, request, redirect, render_template
import mysql.connector as c
import os
from werkzeug.utils import secure_filename
import datetime
from flask_paginate import Pagination, get_page_args

app = Flask(__name__)

user = list()

UPLOAD_FOLDER = 'static/images/product/'

app.secret_key = "secret key"
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024

# Allowed extension of image format
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

# database connection from mysql (ecommerce project database)
db = c.connect(host="localhost", user="root", password="12345", database="ecommerce_project")
if db.is_connected():
    print(True)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


# Check for login of naive users
def check_login():
    global user
    if len(user) == 1:
        return True
    else:
        return False


# Check for admin login then you can switch the admin panel by admin url
def check_admin_login():
    global user
    if len(user) == 1 and user[0][0] == 'admin':
        return True
    else:
        return False


# load the user date at admin panel
def user_data():
    cursor = db.cursor()
    cursor.execute("Select * from user")
    users = cursor.fetchall()
    for i in users:
        print(i)
    return users


# load the product date at admin panel
def product_data():
    cursor = db.cursor()
    cursor.execute("Select * from product")
    products = cursor.fetchall()
    for i in products:
        print(i)
    return products


# pagination at every level when it is required like products or comments.
# this function take pageNumber and get the lower and upper limit of database which have to show on the page.
def pagination(pageNumber):
    pageNumber = int(pageNumber)
    upper = pageNumber * 10
    lower = upper - 10
    return [lower, upper]


# Home page: this is home page if you are login or logout, it doesn't matter. this page is available for all user.
@app.route('/')
@app.route("/home")
def index():
    global user
    username = None
    try:
        username = user[0][0]
    except Exception as e:
        pass

    # fetch the hardware product data with limit 10 from ecommerce_project database
    cursor = db.cursor()
    cursor.execute("Select * from product where p_category='Hardware' limit 10")
    hardware_products = cursor.fetchall()
    # print(hardware_products)

    # fetch the software product data with limit 10 from ecommerce_project database
    cursor = db.cursor()
    cursor.execute("Select * from product where p_category='Software' limit 10")
    software_products = cursor.fetchall()
    # print(software_products)
    return render_template("home.html", username=username, hardware_products=hardware_products,
                           software_products=software_products)


# About page
@app.route("/about")
def about():
    global user
    username = None
    try:
        username = user[0][0]
    except Exception as e:
        pass

    return render_template("about.html", username=username, )


# Contact us page
@app.route("/contactus")
def contactus():
    global user
    username = None
    try:
        username = user[0][0]
    except Exception as e:
        pass

    return render_template("contactus.html", username=username)


products_d = list(product_data())


def get_products(offset=0, per_page=10):
    return products_d[offset: offset + per_page]


# All product are shown order by name
@app.route("/products/")
@app.route("/products_data")
def products(pageNumber=1):
    global user
    username = None
    try:
        username = user[0][0]
    except Exception as e:
        pass
    page, per_page, offset = get_page_args(page_parameter='page',
                                           per_page_parameter='per_page')

    print(type(products_d))
    total = len(products_d)
    print(total)
    pagination_product = get_products(offset=offset, per_page=per_page)
    pagination = Pagination(page=page, per_page=per_page, total=total,
                            css_framework='bootstrap5')

    # #lower, upper = pagination(pageNumber)
    # cursor = db.cursor()
    # cursor.execute("Select * from product;")
    # products = cursor.fetchall()
    #
    return render_template("products.html", username=username,
                           products=pagination_product,
                           category="All",
                           page=page,
                           per_page=5,
                           pagination=pagination)


def get_products_category(offset=0, per_page=10, category='hardware'):
    p_hardware = list()
    for product in products_d:
        cat = str(product[4])
        print(cat)
        if category in cat.lower():
            print(product)
            p_hardware.append(product)
    print(len(p_hardware))

    return [p_hardware[offset: offset + per_page], len(p_hardware)]


# Product category page: here the product are available according to category
@app.route("/products_data/<category>")
def products_category(category):
    global user
    username = None
    try:
        username = user[0][0]
    except Exception as e:
        pass

    page, per_page, offset = get_page_args(page_parameter='page',
                                           per_page_parameter='per_page')

    # print(pageNumber)
    # lower, upper = pagination(pageNumber)
    # cursor = db.cursor()

    # print(type(products_d))
    # total = len(products_d)
    # print(total)
    pagination_product, total = get_products_category(offset=offset, per_page=per_page, category=category)
    print(pagination_product)
    print(total)
    pagination = Pagination(page=page, per_page=per_page, total=total,
                            css_framework='bootstrap5')

    category = category.capitalize()
    return render_template("products.html", username=username,
                           products=pagination_product,
                           category=category,
                           page=page,
                           per_page=10,
                           pagination=pagination)


# product page: where you can see all the product detail and add to cart option if you have login to the account
@app.route("/product/<productId>", methods=['POST', 'GET'])
def product_page(productId):
    global user
    username = None
    try:
        username = user[0][0]
    except Exception as e:
        pass

    cursor = db.cursor()
    cursor.execute("Select * from product where p_id='{}'".format(productId))
    product_info = cursor.fetchall()
    # print(product_info)
    alert = ""

    cursor = db.cursor()
    cursor.execute(
        "select name,date,comment,helpful from comments join user on user.username=comments.username where p_id='{}' order by helpful limit 0,5;".format(
            productId))
    comments = cursor.fetchall()
    # print(comments)
    # comments=[]

    # Adding the product in the cart using product id and username
    if request.method == 'POST':
        quantity = request.form['quantity']
        if username is not None:
            print(quantity, productId, username)

            # check the cart for username and product id is already add in cart or not?
            cursor = db.cursor()
            cursor.execute("select * from cart where username='{}' and p_id='{}'".format(username, productId))
            fetch = cursor.fetchall()

            if len(fetch) == 0:
                # cursor = db.cursor()
                print(product_info[0][2])
                price = int(quantity) * product_info[0][2]
                print(price)

                query = "insert into cart value('" + username + "', '" + productId + "'," + str(quantity) + "," + str(
                    price) + ");"
                print(query)
                cursor.execute(query)
                db.commit()
                print("Successfully add to cart")
                alert = "Successfully add to cart"
            else:
                alert = "Already in cart"
        else:
            alert = "You have to login first"
            print(quantity, productId)

    # Adding comments in product you can add only one comment in the unique product.
    if request.method == 'GET':
        com = request.args.get("comment")
        p_id = request.args.get("p_id")
        t = datetime.datetime.now()
        print(t)
        print(t.year)
        print(t.month)
        print(t.day)
        date = str(t.year) + "-" + str(t.month) + "-" + str(t.day)
        helpful = 0
        print(com, username, p_id, date)
        if username is None:
            pass
        else:
            cursor = db.cursor()
            print("Updating the comments table")
            query = "insert into comments values('{}','{}','{}',0,'{}');".format(username, p_id, com, date)
            print(query)
            try:
                cursor.execute(query)
                print("Comments table has been updated")
                db.commit()
                return redirect(request.referrer)
            except Exception as e:
                print(e)

    return render_template("product_page.html", username=username, productId=productId, product_info=product_info,
                           alert=alert, comments=comments)


# Show add the comments of user by using product id
@app.route("/product/<productId>/comments")
def all_comments(productId):
    global user
    username = None
    try:
        username = user[0][0]
    except Exception as e:
        pass

    cursor = db.cursor()
    cursor.execute(
        "select name,date,comment,helpful from comments join user on user.username=comments.username where p_id='{}' order by helpful;".format(
            productId))
    comments = cursor.fetchall()

    return render_template("comments.html", username=username,
                           comments=comments)



def get_products_search(offset=0, per_page=10, name=''):
    p_result = list()
    if name == '':
        return [p_result, len(p_result)]
    for product in products_d:
        cat = str(product[1])
        print(cat)
        if name in cat.lower():
            print(product)
            p_result.append(product)
    print(len(p_result))

    return [p_result[offset: offset + per_page], len(p_result)]

# Search by name
@app.route("/search", methods=['POST', 'GET'])
@app.route("/search/<name>")
def search(name=""):
    global user
    username = None
    try:
        username = user[0][0]
    except Exception as e:
        pass

    if request.method == 'POST':
        name = request.form['search']
        print(name)

    page, per_page, offset = get_page_args(page_parameter='page',
                                           per_page_parameter='per_page')

    # print(type(products_d))
    # total = len(products_d)
    # print(total)
    pagination_product, total = get_products_search(offset=offset, per_page=per_page, name=name)
    print(pagination_product)
    print(total)
    pagination = Pagination(page=page, per_page=per_page, total=total,
                            css_framework='bootstrap5')

    return render_template("products.html", username=username,
                           products=pagination_product,
                           category="All",
                           page=page,
                           per_page=10,
                           pagination=pagination)


    # cursor = db.cursor()
    # cursor.execute("Select * from product where  p_name like'%{}%'".format(name))
    # products = cursor.fetchall()
    # print(products)

    # return render_template("products.html", username=username, products=products, category="Result")


# login page
@app.route("/login", methods=['POST', 'GET'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        print(email, password)

        cursor = db.cursor()

        cursor.execute("Select * from user where email='{}' and password='{}'".format(email, password))
        global user
        user = cursor.fetchall()
        print(user)
        print(type(user))
        if len(user) == 1:
            print("Longin successfully")
            return redirect("/home")
        else:
            return redirect("/")

    return render_template("login.html")


# logout page: After logout redirect to home page
@app.route("/logout")
def logout():
    global user
    if len(user) == 1:
        user.pop()
    return redirect('/home')


# sign page: fill the detail and sign in redirect to thank you for sign in page
@app.route("/signup")
def signup():
    return render_template("signup.html")


# thank you: thank you page is available when user has first sign in.
@app.route("/thankyou", methods=['POST', 'GET'])
def thankyou():
    if request.method == 'POST':
        data = request.form.to_dict()

        print(data)
        db = c.connect(host="localhost", user="root", password="12345", database="ecommerce_project")
        cursor = db.cursor()

        cursor.execute("insert into user values ('{}','{}','{}', '{}','{}');".format(data['username'], data['name'],
                                                                                     data['address'], data['email'],
                                                                                     data['password']))
        db.commit()
        return render_template("thankyou.html", name=data['username'])


@app.route("/cart/<userName>", methods=['POST', 'GET'])
def cart(userName):
    global user
    username = None
    try:
        username = user[0][0]
    except Exception as e:
        pass

    cursor = db.cursor()
    cursor.execute(
        "select p_name,p_price,quantity,p_image, (p_price*quantity) sub_total,cart.p_id from cart join product on cart.p_id=product.p_id where username='{}';"
        .format(username))
    carts = cursor.fetchall()
    for i in carts:
        print(i)

    product_sum = 0
    for cart in carts:
        product_sum = product_sum + int(cart[4])
    print(product_sum)

    shipping = 40

    total_sum = product_sum + shipping

    if request.method == "POST":
        cursor = db.cursor()
        print("--------------------------------")
        print(username)
        productId = request.form.to_dict()
        productId = productId['productId']
        print(productId)

        cursor.execute("delete from cart where username='{}' and p_id='{}';".format(username, productId))
        db.commit()
        print("delete success")
        return redirect("/cart/productId")

    return render_template("cart.html", username=username, carts=carts, total_sum=total_sum, shipping=shipping,
                           product_sum=product_sum, number_of_items=len(carts))


# TODO: add login change
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


@app.route("/company_data")
def company_data():
    global user
    username = None
    try:
        username = user[0][0]
    except Exception as e:
        pass
    if check_admin_login():
        cursor = db.cursor()
        cursor.execute("Select * from company")
        company = cursor.fetchall()
        for i in company:
            print(i)

        return render_template("company_data.html", company=company, username=username)
    return redirect("/login")


def update_product():
    global products_d
    cursor = db.cursor()
    cursor.execute("select * from product;")
    products_d = cursor.fetchall()


@app.route("/product_data/",  methods=['POST', 'GET'])
def product_data():
    global user
    username = None
    try:
        username = user[0][0]
    except Exception as e:
        pass

    if check_admin_login():
        # product = product_data()
        db = c.connect(host="localhost", user="root", password="12345", database="ecommerce_project")
        if db.is_connected():
            print(True)
        cursor = db.cursor()
        cursor.execute("Select * from product")
        products = cursor.fetchall()
        for i in range(len(products)):
            print(products[i])

        if (request.method == "POST"):
            data = request.form.to_dict()
            print(data)
            f = request.files['image']
            # f.save()
            filename = data['productid'] + '.' + secure_filename(f.filename.split(".")[-1])

            f.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

            print(data)
            db = c.connect(host="localhost", user="root", password="12345", database="ecommerce_project")
            if db.is_connected():
                print(True)

            cursor = db.cursor()

            cursor.execute("insert into product values ('{}','{}','{}', '{}','{}','{}','{}');".format(data['productid'],
                                                                                                      data[
                                                                                                          'product_name'],
                                                                                                      data['price'],
                                                                                                      data['detail'],
                                                                                                      data['category'],
                                                                                                      data[
                                                                                                          'company_id'],
                                                                                                      str(os.path.join(
                                                                                                          app.config[
                                                                                                              'UPLOAD_FOLDER']) + filename)))
            db.commit()
            update_product()
            return redirect(request.referrer)
        return render_template("product_data.html", products=products, username=username, length=len(products))
    return redirect("/login")


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
        cursor = db.cursor()
        cursor.execute("Select * from user")
        users = cursor.fetchall()
        for i in users:
            print(i)
        # users = user_data()
        return render_template("user_data.html", username=username, users=users)
    return redirect("/login")

if __name__ == '__main__':
    app.run(debug=True)
