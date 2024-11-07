from flask import Blueprint, render_template,request,flash

auth = Blueprint('auth',__name__)




@auth.route('/login', methods=['GET','POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('profile'))
    form = LoginForm()
    if form.validate_on_submit():
        with sqlite3.connect('login.db') as conn:
            curs = conn.cursor()
            curs.execute("SELECT * FROM login WHERE email = ?", (form.email.data,))
            user_data = curs.fetchone()
        if user_data:
            user = load_user(user_data[0])
            if user and user.password == form.password.data:
                login_user(user, remember=form.remember.data)
                flash(f'Logged in successfully as {form.email.data.split("@")[0]}')
                return redirect(url_for('profile'))
            else:
                flash('Login unsuccessful. Check your credentials and try again.')
        else:
            flash('No account found with that email.')
    return render_template('login.html', title='Login', form=form)



@auth.route('/logout')
def logout():
    return render_template("logout.html")

@auth.route('/sign', methods=['GET', 'POST'])
def sign_up():
    if request.method == 'POST':
        email = request.form.get('email')
        firstName = request.form.get('firstName')
        password1 = request.form.get('password1')
        password2 = request.form.get('password2')

        # Perform validation checks within the POST request scope
        if len(email) < 2:
            flash('Email length must be more than 2 characters', category="error")
            print("email"),
        elif len(firstName) < 1: 
            flash('First Name length must be more than 1 character', category="error")
        elif password1 != password2:
            flash('Passwords do not match', category="error")
        elif len(password1) < 8:
            flash('Password must have more than 8 characters', category="error")
        else:
            flash('Successfully created account!', category="success") 
    return render_template("sign_up.html")

