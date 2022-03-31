from flask import render_template, url_for, flash, redirect, request, abort
from crop_app import app, bcrypt
from crop_app.forms import RegistrationForm, LoginForm, UpdateAccountForm, PostForm
from crop_app.models import User
import requests, json, secrets, os
from flask_login import login_user, current_user, logout_user, login_required
from PIL import Image

posts = [
    {
        'author': 'John Brian F. Quebral',
        'title': 'Update Version 0.9',
        'content': """Added the Forum for posting new updates
                      from different farmers around the country.
                      They can also Update and Delete the posts
                      created by the owners.""",
        'date_posted': 'March 14, 2022'
    },
    {
        'author': 'John Brian F. Quebral',
        'title': 'Update Version 0.7',
        'content': """Created a table for the soil testing 
                      parameters such as Nitrogen, Phosphorous,
                      Potassium and pH Level and show the details
                      such as the time the soil is tested and the
                      real-time recommended crops.""",
        'date_posted': 'March 1, 2022'
    },
    {
        'author': 'John Brian F. Quebral',
        'title': 'Update Version 0.65',
        'content': """Deployed the sample web application in 
                      the Heroku Free Cloud Deployment Website 
                      and committed the application and API.""",
        'date_posted': 'February 21, 2018'
    }
]

@app.route("/")
def welcome():
    return render_template("welcome.html", posts=posts)

@app.route('/recommendations')
@login_required
def recommendations():
    response = requests.get('https://api01crop.herokuapp.com/recommendation')
    table_list = []
    for data in response.json():
        table_list.append(data)
    return render_template("recom_list.html", title="Recommendations", data=table_list)

@app.route("/about")
def about():
    return render_template("about.html", title="About")

@app.route("/developers")
def developers():
    return render_template("developers.html", title="Developers")

@app.route("/dashboard")
@login_required
def dashboard():
    return render_template("dashboard.html", title="Dashboard")

@app.route("/forums")
@login_required
def forums():
    response = requests.get('https://api01crop.herokuapp.com/get_posts')
    post = []
    for row in response.json():
        post.append(row)
    return render_template("forums.html", title="Forums", posts=post)

@app.route("/register", methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('welcome'))
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_pw = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        new_user_dict = {
                            'user_fname':form.fname.data,
                            'user_mname':form.mname.data,
                            'user_lname':form.lname.data,
                            'username':form.username.data,
                            'email':form.email.data,
                            'password':hashed_pw
                        }
        new_user_json = json.dumps(new_user_dict, indent=4)
        headers = {'Content-type':"application/json"}
        response = requests.post('https://api01crop.herokuapp.com/create', headers=headers, data=new_user_json)
        if response.status_code == 200:
            flash('You have successfully created an Account!', 'success')
            return redirect(url_for('login'))
    return render_template('register.html', title="Register", form=form)

@app.route("/login", methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('welcome'))
    form = LoginForm()
    if form.validate_on_submit():
        user = requests.get(f'https://api01crop.herokuapp.com/existing_username/?username={form.username.data}')
        data = user.json()
        if data != {}:
            username = data['username']
            password = data['password']
        else:
            username = False
        if username:
            if bcrypt.check_password_hash(password, form.password.data):
                user_login = User(user)
                login_user(user_login, remember=form.remember.data)
                next_page = request.args.get('next')
                flash("You have been logged in!", 'success')
                return redirect(next_page) if next_page else redirect(url_for('dashboard'))
            else:
                flash('Login Unsuccessful. Please check username and password!', 'danger')
    return render_template('login.html', title="Login", form=form)

@app.route('/account')
@login_required
def account():
    image_file = url_for('static', filename='profile_pics/' + current_user.user_image)
    return render_template('account.html', title="Account", image_file=image_file)

def save_image(form_image):
    random_hex = secrets.token_hex(8)
    _, f_ext = os.path.splitext(form_image.filename)
    image_filename = random_hex + f_ext
    image_path = os.path.join(app.root_path, 'static/profile_pics', image_filename)
    
    output_size = (125, 125)
    i = Image.open(form_image)
    i.thumbnail(output_size)
    i.save(image_path)

    return image_filename

@app.route('/update_account', methods=['GET', 'POST'])
@login_required
def update_account():
    form = UpdateAccountForm()
    if form.validate_on_submit():
        if form.image.data:
            image_file = save_image(form.image.data)
        else:
            image_file = 'default.jpg'
        new_user_dict = {
                            'user_fname':form.fname.data,
                            'user_mname':form.mname.data,
                            'user_lname':form.lname.data,
                            'username':form.username.data,
                            'email':form.email.data,
                            'user_image':image_file
                        }
        updated_account_json = json.dumps(new_user_dict, indent=4)
        headers = {'Content-type':"application/json"}
        requests.put(f'https://api01crop.herokuapp.com/update_account/{current_user.user_id}', 
                     headers=headers, 
                     data=updated_account_json)
        flash('Your Account has been Updated!', 'success')
        return redirect(url_for('account'))
    elif request.method == 'GET':
        form.fname.data = current_user.user_fname
        form.mname.data = current_user.user_mname
        form.lname.data = current_user.user_lname
        form.username.data = current_user.username
        form.email.data = current_user.email
        form.image.data = current_user.user_image
    return render_template('update_info.html', title="Update Account",
                            form = form)

@app.route("/post/new", methods=['POST', 'GET'])
#@login_required
def new_post():
    form = PostForm()
    if form.validate_on_submit():
        new_post_dict = {
                            "title": form.title.data,
                            "content": form.content.data,
                            "author" : current_user.user_id
                        }
        new_post_json = json.dumps(new_post_dict, indent=4)
        headers = {'Content-type':"application/json"}
        response = requests.post('https://api01crop.herokuapp.com/new_post', 
                                headers=headers, 
                                data=new_post_json)
        if response.status_code == 200:
            flash('Your post has been created!', 'success')
            return redirect(url_for('forums'))
    return render_template('create_post.html', title="New Post", 
                            form=form, legend="New Post")

@app.route("/post/<int:post_id>")
@login_required
def post(post_id):
    response = requests.get(f'https://api01crop.herokuapp.com/post/{post_id}')
    post = response.json()
    return render_template("post_spec.html", title=post['title'], post=post)

@app.route("/update_post/<int:post_id>", methods=['GET', 'POST'])
@login_required
def update_post(post_id):
    response = requests.get(f'https://api01crop.herokuapp.com/post/{post_id}')
    post = response.json()
    if post['author']['email'] != current_user.email:
        abort(403)
    form = PostForm()
    if form.validate_on_submit():
        update_title = form.title.data
        update_content = form.content.data
        update_post_dict = {
                                "title": update_title,
                                "content": update_content
                            }
        update_post_json = json.dumps(update_post_dict, indent=4)
        headers = {'Content-type':"application/json"}
        requests.put(f"https://api01crop.herokuapp.com/update_post/{post['id']}", 
                     headers=headers,
                     data=update_post_json)
        flash('Your Post has been Updated!', 'success')
        return redirect(url_for('post',post_id=post['id']))
    elif request.method == "GET":
        form.title.data = post['title']
        form.content.data = post['content']
    return render_template('create_post.html', title="Update Post",
                             form=form, legend="Update Post")

@app.route("/delete_post/<int:post_id>", methods=['POST'])
@login_required
def delete_post(post_id):
    response = requests.get(f'https://api01crop.herokuapp.com/post/{post_id}')
    post = response.json()
    if post['author']['email'] != current_user.email:
        abort(403)
    requests.delete(f'https://api01crop.herokuapp.com/delete_post/{post_id}')
    flash('Your post has been deleted!', 'success')
    return redirect(url_for('forums'))

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('welcome'))