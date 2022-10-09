import mysql.connector as c

db = c.connect(host="localhost",user="root", password="12345", database="ecommerce_project")

if db.is_connected():
    print(True)

def cart_count(username):
    cursor = db.cursor()
    query = "select count(*) from cart where username='{}';"
    cursor.execute(query.format(username))
    cart = cursor.fetchall()
    cart = cart[0][0]
    print(cart)
    return cart

# pagination at every level when it is required like products or comments.
# this function take pageNumber and get the lower and upper limit of database which have to show on the page.
def pagination(pageNumber):
    pageNumber = int(pageNumber)
    upper = pageNumber * 10
    lower = upper - 10
    return [lower, upper]

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

def cart_item(username):
    cursor = db.cursor()
    cursor.execute(
        "select p_name,p_price,quantity,p_image, (p_price*quantity) sub_total,cart.p_id from cart join product on cart.p_id=product.p_id where username='{}';"
        .format(username))
    carts = cursor.fetchall()
    return carts