from flask import Flask, render_template, session, request, redirect, g, flash, url_for
from flask import Flask, Request
from flask_bootstrap import Bootstrap
from twilio.rest import Client
import os, random
import pymysql

app = Flask(__name__)
Bootstrap(app)
app.secret_key = os.urandom(24)
app.config['STRIPE_PUBLIC_KEY']='pk_test_51IXPhESDcO8lL4YQo9a4P699rQrEV6X5CGQZJpqFj1gxEeg8BVPS6GypUkVaJNkCHRgiKuJ3XLBFc598Mc9E1vAJ009wTZimbs'
app.config['STRIPE_SECRET_KEY']='sk_test_51IXPhESDcO8lL4YQldzIIP4fqMNHbXsssNGzAGmUPyjNT8maAyfmcCuIwbN9G3Iwk31fi69jTwyBv1NUiOdgy3o200Dx5ela6J'
db = pymysql.connect("localhost", "root", "vedant151617", "flaskapp")
cursor = db.cursor()




def getOTPApi(number):
    otp = random.randint(1000, 9999)
    account_sid = "AC0923eb520c0a211f5728496160b78667"
    auth_token = "db4c74b44d24ee4f09a61ce616521a90"
    client = Client(account_sid, auth_token)
    message = client.messages.create(
        body="Hello,your OTP for the payment checkout is" + str(otp),
        from_="+17067058245",
        to="+91" + number
    )
    print(message.sid)
    return otp


@app.route("/Loginsignup", methods=['GET', 'POST'])
def home():
    if request.method == 'POST' and 'login' in request.form:
        email = request.form.get('lemail')
        password = request.form.get('lpassword')
        cursor.execute(
            """SELECT email FROM appusers WHERE email LIKE '{}' AND password LIKE '{}'  """.format(email, password))
        userexists = cursor.fetchall()
        if len(userexists) > 0:
            session.pop('user', None)
            session['user'] = email
            print(type(session["user"]))
            return redirect('/')
        else:
            flash('Email already exists', 'InvalidUser')
    if request.method == 'POST' and 'signup' in request.form:
        semail = request.form.get('email')
        spassword = request.form.get('password')
        cnfpassword = request.form.get('cnfpassword')
        name = request.form.get('name')
        phone = request.form.get('phone')
        cursor.execute("""SELECT email FROM appusers WHERE email LIKE '{}'  """.format(semail))
        users = cursor.fetchall()
        print(users)
        print(len(users))
        if len(users) != 0:
            flash('User already exists', 'UserExistsError')
        else:
            if spassword == cnfpassword:
                insquery = """INSERT INTO appusers(Name,email,password,phone,address)values(%s,%s,%s,%s,%s)"""
                val = (name, semail, spassword, phone, '')
                cursor.execute(insquery, val)
                db.commit()
                flash('Signup Successfull', 'SignupSuccess')
            else:
                flash('Email already exists', 'passwordNotMatchingError')
    return render_template('Loginsignup.html')


@app.before_request
def before_request():
    g.user = None
    if 'user' in session:
        g.user = session['user']


@app.route("/", methods=['GET', 'POST'])
def mobiles():
    pro_id = request.form.get('pid')
    cursor.execute("""SELECT * from products where Pcategory='Mobiles'""")
    data = cursor.fetchall()
    cursor.execute("SELECT * from categories")
    cat = cursor.fetchall()
    db.commit()
    if g.user:
        cursor.execute('SELECT count(*) from cart')
        total_no_of_items = cursor.fetchall()
        if pro_id and request.method == 'POST':
            pro_name = request.form.get('pname')
            pro_price = int(request.form.get('pprice'))
            quantity = int(request.form.get('quantity'))
            tot_price = quantity * pro_price
            sql = "insert into cart(id,name,unit_price,quantity,tot_price) values(%s,%s,%s,%s,%s)"
            vals = (pro_id, pro_name, pro_price, quantity, tot_price)
            cursor.execute(sql, vals)
            db.commit()
        return render_template('Mobiles.html', product=data, total_items=total_no_of_items[0][0],category=cat)
        
    else:
        cursor.execute("DELETE from cart")
        db.commit()
        return redirect('/Loginsignup')


@app.route("/Laptops", methods=['GET', 'POST'])
def laptops():
    pro_id = request.form.get('pid')
    cursor.execute("""SELECT * from products where Pcategory='Laptops'""")
    data = cursor.fetchall()
    cursor.execute('SELECT count(*) from cart')
    total_no_of_items = cursor.fetchall()
    db.commit()
    if g.user:
        if pro_id and request.method == 'POST':
            pro_name = request.form.get('pname')
            pro_price = int(request.form.get('pprice'))
            quantity = int(request.form.get('quantity'))
            tot_price = quantity * pro_price
            sql = "insert into cart(id,name,unit_price,quantity,tot_price) values(%s,%s,%s,%s,%s)"
            vals = (pro_id, pro_name, pro_price, quantity, tot_price)
            cursor.execute(sql, vals)
            db.commit()
        return render_template('Laptops.html', product=data,total_items=total_no_of_items[0][0])
    else:
        cursor.execute("DELETE from cart")
        db.commit()
        return redirect('/Loginsignup')


@app.route("/emptycart", methods=['GET', 'POST'])
def emptyCart():
    flash('Email already exists', 'InvalidUser')
    return render_template('emptycart.html')


@app.route("/mycart", methods=['GET', 'POST'])
def mycart():
    cursor.execute('SELECT * from cart')
    data = cursor.fetchall()
    cursor.execute('SELECT sum(tot_price) from cart')
    total = cursor.fetchall()
    cursor.execute("SELECT * from categories")
    cat = cursor.fetchall()
    cursor.execute('SELECT count(*) from cart')
    total_no_of_items = cursor.fetchall()
    db.commit()
    if data != ():
        return render_template('mycart.html', items=data, total=int(total[0][0]),category=cat,total_items = total_no_of_items[0][0])
    else:
        return redirect('/emptycart')



@app.route("/payment", methods=['GET', 'POST'])
def payment():
    cursor.execute('SELECT * from cart')
    data = cursor.fetchall()
    cursor.execute('SELECT sum(tot_price) from cart')
    total = cursor.fetchall()
    cursor.execute('SELECT count(*) from cart')
    total_no_of_items = cursor.fetchall()
    cursor.execute("SELECT * from categories")
    cat = cursor.fetchall()
    db.commit()
    if g.user:
        if request.method == 'POST':
            return redirect('/verifyotp')
    return render_template('payment.html', items=data, total=str(float(total[0][0])), total_items=total_no_of_items[0][0],category=cat)


@app.route("/verifyotp", methods=['GET', 'POST'])
def verifyOTP():
    otp = request.form.get('otp')
    cursor.execute("SELECT * from categories")
    cat = cursor.fetchall()
    cursor.execute('SELECT count(*) from cart')
    total_no_of_items = cursor.fetchall()
    cursor.execute("""SELECT phone from appusers where email LIKE '{}' """.format(session["user"]))
    number = cursor.fetchall()
    val = getOTPApi(number[0][0])
    if request.method == 'POST':
        if otp == val:
            cursor.execute("DELETE from cart")
            db.commit()
            return redirect('/success')
    return render_template('verifyOTP.html',category=cat,total=total_no_of_items)


@app.route("/success", methods=['GET', 'POST'])
def sucess():
    cursor.execute('SELECT * from cart')
    data = cursor.fetchall()
    cursor.execute('SELECT sum(tot_price) from cart')
    total_price = cursor.fetchall()
    cursor.execute('SELECT count(*) from cart')
    total_no_of_items = cursor.fetchall()
    cursor.execute("SELECT * from categories")
    cat = cursor.fetchall()
    db.commit()
    return render_template('success.html', items=data, total_price=int(total_price[0][0]),total=total_no_of_items,category=cat)


@app.route("/addprod", methods=['GET', 'POST'])
def AddProducts():
    path = "./static/laptops/"
    proid = request.form.get('proid')
    proname = request.form.get('proname')
    proprice = request.form.get('proprice')
    procatid = request.form.get('procatid')
    procat = request.form.get('procat')
    bname = request.form.get('bname')
    qty = request.form.get('qty')
    img = request.form.get('img')
    totalpath = path + str(img)
    cursor.execute('select * from categories')
    data = cursor.fetchall()
    if request.method == 'POST':
        status = 1
        sql = """insert into products(Pname,Pprice,Pcategory,Pbrand,qty,image,status)values(%s,%s,%s,%s,%s,%s,%s)"""
        vals = (proname, proprice, procat, bname, qty, totalpath, status)
        cursor.execute(sql, vals)
        db.commit()
    return render_template('AddProducts.html', prodcat=data)


@app.route("/index", methods=['GET', 'POST'])
def index():
    return render_template('index.html')


@app.route("/addcat", methods=['GET', 'POST'])
def AddCategories():
    if request.method == 'POST':
        catname = request.form.get('catname')
        cursor.execute("""SELECT CatName from categories where CatName like '{}' """.format(catname))
        catisexixts = cursor.fetchall()
        if len(catisexixts) != 0:
            flash('User already exists', 'CategoryExists')
        else:
            values = (catname, 1)
            catins = """INSERT INTO categories(CatName,catStatus) values(%s,%s)"""
            cursor.execute(catins, values)
            db.commit()
            flash('User already exists', 'CategorySuccess')
    return render_template('AddCategories.html')


@app.route("/products", methods=['GET', 'POST'])
def Products():
    catname = request.form.get('cat_name')
    cursor.execute('SELECT * from products')
    data = cursor.fetchall()
    db.commit()
    return render_template('Products.html', prod=data)


@app.route("/updateprod", methods=['GET', 'POST'])
def updateprod():
    if request.method == 'POST':
        path = "./static/mobiles/"
        id_data = request.form.get('id')
        proname = request.form.get('proname')
        proprice = request.form.get('proprice')
        pcategory = request.form.get('pcategory')
        bname = request.form.get('bname')
        qty = request.form.get('qty')
        img = request.form.get('img')
        totalpath = path + str(img)
        cursor.execute("""UPDATE products set Pname=%s,Pprice=%s,Pcategory=%s,Pbrand=%s,qty=%s,image=%s where Pid=%s""",
                       (proname, proprice, pcategory, bname, qty, totalpath, id_data))
        return redirect(url_for('Products'))


@app.route("/deleteprod/<string:id_data>", methods=['GET', 'POST'])
def deleteprod(id_data):
    id_data = request.form.get('id')
    cursor.execute("DELETE from products where Pid='%s'", (id_data))
    db.commit()
    return redirect(url_for('Products'))


@app.route("/cat", methods=['GET', 'POST'])
def categories():
    catname = request.form.get('ac')
    cursor.execute('SELECT * from categories')
    data = cursor.fetchall()
    cursor.execute(""" DELETE from categories where CatName like '{}' """.format(catname))
    db.commit()
    return render_template('categories.html', cat=data)


@app.route("/update", methods=['GET', 'POST'])
def catUpdate():
    cat = request.form.get('cat_name')
    ucatname = request.form.get('ucatname')
    values = (ucatname, cat)
    sql = "update categories set CatName= '%s' where CatName = '%s'"
    cursor.execute(sql, values)
    return render_template('ManageCategories.html')


@app.route("/OurProducts", methods=['GET', 'POST'])
def OurProducts():
    if g.user:
        return render_template('OurProducts.html', user=session['user'])
    return redirect('/Loginsignup')


if __name__ == '__main__':
    app.run()
