from flask.globals import request
import sqlalchemy
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm import scoped_session
from project_orm import User
import advertools as adv
from flask import Flask, session, flash, render_template, redirect, url_for
import re
app = Flask(__name__)
app.secret_key = "the basics of life with python"
import pandas as pd
import os
def get_db():
    engine = create_engine('sqlite:///database.db')
    Session = scoped_session(sessionmaker(bind=engine))
    return Session()


# for validating an Email 
def validate_email(email):  
    regex = '^[a-z0-9]+[\._]?[a-z0-9]+[@]\w+[.]\w{2,3}$'
    if(re.search(regex,email)):  
        return True 
    return False


@app.route('/' ,methods = ['GET', 'POST'])
def index():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        print(email, password )
        if password and len(password) >= 6:
            if email and validate_email(email):
                try:
                    sess = get_db()
                    user = sess.query(User).filter_by(email=email,password=password).first()
                    if user:
                        session['isauth'] = True
                        session['email'] = user.email
                        session['id'] = user.id
                        session['name'] = user.username
                        del sess
                        flash('login successfull','success')
                        return redirect('/home')
                    else:
                        flash('email or password is wrong','danger')
                except Exception as e:
                    print(e)
                    flash('email account not exists','danger')
            else:
                flash('invalid email','danger')
        else:
            flash('password must be of 6 or more characters','danger')
    return render_template('index.html', title='login')

@app.route('/signup' ,methods = ['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form.get('name')
        email = request.form.get('email')
        password = request.form.get('password')
        cpassword = request.form.get('password')
        print(username, email, password, cpassword)
        if username and len(username)>= 3:
            if email and validate_email(email):
                if password and len(password) >= 6:
                    if cpassword and cpassword == password:
                        try:
                            sess = get_db()
                            newuser = User(username=username,email=email,password=password)
                            sess.add(newuser)
                            sess.commit()
                            flash('registration successful','success')
                            return redirect('/')
                        except Exception as e:
                            print(e)
                            flash('email account already exists','danger')
                    else:
                        flash('confirm password does not match','danger')
                else:
                    flash('password must be of 6 or more characters','danger')
            else:
                flash('invalid email','danger')
        else:
            flash('invalid name, must be 3 or more characters','danger')

    return render_template('signup.html', title='registration')

@app.route('/home', methods=['GET','POST'])
def home():
    return render_template('home.html',title='home')


@app.route('/contact', methods=['GET','POST'])
def contact():
    return render_template('/contact.html')

@app.route('/about', methods=['GET','POST'])
def about():
    return render_template('/about.html')

@app.route('/keywords', methods=['GET','POST'])
def keywords():
    if request.method == 'POST':
        words = request.form.get('words')
        products = request.form.get('product')
        words = [name.strip().lower() for name in words.split(',')]
        products = [name.strip().lower() for name in products.split(',')]
        kw_df = adv.kw_generate(products, words)
        print(kw_df.head())
        keyword_list = kw_df['Keyword'].tolist()
        return render_template('keywords_result.html', data= kw_df.to_html(), kl = keyword_list)
    else:
        print('showing form')
    return render_template('keywords.html')

@app.route('/logout')
def logout():
    if 'isauth' in session:
        session['isauth'] = None
    return render_template('/home')

@app.route('/searchseo')
def search_seo():
    if request.method == "GET":
        url = request.args.get('url')
        filepath = url.replace('.','').replace('http','').replace(":",'').replace('https','').replace("_",'').replace("-","_").replace('/','')+".jl"
        filepath = os.path.join('static','crawls', filepath)
        print("filepath",filepath)
        adv.crawl(url, filepath , follow_links=False)
        session['seo_file'] = filepath
        session['url'] = url
        try:
            crawl_df = pd.read_json(filepath, lines=True)
            print(crawl_df.head())
            return render_template('result_seo.html', results = crawl_df.T.to_html())
        except Exception as e:
            print('error',e)
    return redirect('/home')


@app.route('/display/seo')
def display_data():
    files = os.listdir(os.path.join("static",'crawls'))
    files = [os.path.join("static",'crawls',f) for f in files if '.jl' in f]
    print(files)
    return render_template('display.html', files = files)

@app.route('/display/dataframe')
def display_dataframe():
    file = request.args.get('file')
    crawl_df = pd.read_json(f'{file}', lines=True)
    print(crawl_df.head())
    return render_template('data.html', results = crawl_df.T.to_html())

if __name__ == '__main__':
  app.run(host='127.0.0.1', port=8000, debug=True)