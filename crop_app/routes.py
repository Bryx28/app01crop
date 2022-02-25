from flask import render_template, url_for, flash, redirect, request
from crop_app import app, bcrypt
from crop_app.forms import RegistrationForm, LoginForm, UpdateAccountForm
from crop_app.models import User
import requests, json, secrets, os
from flask_login import login_user, current_user, logout_user, login_required
from PIL import Image

posts = [
    {
        'author': 'Corey Schafer',
        'title': 'Blog Post 1',
        'content': 'First post content',
        'date_posted': 'April 20, 2018'
    },
    {
        'author': 'Jane Doe',
        'title': 'Blog Post 2',
        'content': 'Second post content',
        'date_posted': 'April 21, 2018'
    }
]

@app.route("/")
def welcome():
    return render_template("welcome.html", posts=posts)

@app.route('/recommendations')
@login_required
def recommendations():
    date = ["03/02/22", "03/01/22", "02/22/22", "02/21/22"]
    dn = ["RM-22-0001", "RM-22-0004", "RM-22-0005", "RM-22-0001"]
    recom = ["Maize", "Rice", "Rice", "Corn"]
    nitro = [22, 23, 22, 12]
    phos = [65, 24, 33, 22]
    kpos = [12, 22, 32, 44]
    phL = [6.7, 6.2, 7.1, 6.3]
    table_list = []
    for a in range(len(date)):
        table_list.append({'date': date[a],
                            'dn': dn[a],
                            'recom': recom[a],
                            'nitro': nitro[a],
                            'phos': phos[a],
                            'kpos': kpos[a],
                            'phL':phL[a]})
    return render_template("recommendation.html", title="Recommendations", data=table_list)

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
        user = requests.get(f'https://api01crop.herokuapp.com/existing_username/{form.username.data}')
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
        new_user_json = json.dumps(new_user_dict, indent=4)
        headers = {'Content-type':"application/json"}
        requests.put(f'https://api01crop.herokuapp.com/update_account/{current_user.user_id}', 
                     headers=headers, data=new_user_json)
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

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('welcome'))