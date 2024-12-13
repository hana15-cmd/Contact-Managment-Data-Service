
# from flask import Blueprint, current_app, flash, redirect, render_template, request, url_for
# from flask_login import login_required
# import sqlite3 as sql

# from database_logic.models import add_dummy_contacts_data, admin_required
# from forms import AddTeamMemberForm, EditTeamMemberForm


# employees = Blueprint('employees', __name__)


# @employees.route("/see_team_members/<string:id>", methods=['POST', 'GET'])
# @login_required
# def see_team_members(id):
#     # Validate the ID
#     if not id.isdigit():
#         flash("Invalid team ID.", "danger")
#         return redirect(url_for("views.contacts"))

#     con = sql.connect(current_app.config['DATABASE'])
#     con.row_factory = sql.Row
#     try:
#         cur = con.cursor()

#         # Fetch team details
#         cur.execute("SELECT * FROM teams WHERE ID=?", (id,))
#         team = cur.fetchone()

#         if not team:
#             flash(f"No team found with ID {id}.", "danger")
#             return redirect(url_for("views.contacts"))

#         # Fetch team members
#         cur.execute("SELECT * FROM contacts WHERE team_id=?", (id,))
#         members = cur.fetchall()

#         if not members:
#             flash("No members found for this team. Adding dummy members for testing.", "info")

#             # Call the add_dummy_contacts_data function to insert dummy data
#             add_dummy_contacts_data()

#             # Refresh the members list after inserting dummy data
#             cur.execute("SELECT * FROM contacts WHERE team_id=?", (id,))
#             members = cur.fetchall()

#         # Render the template with team and member details
#         return render_template("employee_table/team_member_info.html", team=team, members=members)
#     except Exception as e:
#         flash("An unexpected error occurred. Please try again later.", "danger")
#         return redirect(url_for("views.contacts"))
#     finally:
#         if con:
#             con.close()


# @employees.route("/create/<int:team_id>", methods=['POST', 'GET'])
# @login_required
# def add_team_member(team_id):
#     form = AddTeamMemberForm()

#     # Fetch teams to populate the select field
#     con = sql.connect(current_app.config['DATABASE'])
#     con.row_factory = sql.Row
#     cur = con.cursor()
#     cur.execute("SELECT id, team_name FROM teams")
#     teams = cur.fetchall()
#     con.close()

#     # Populate the team select field choices
#     form.team_id.choices = [(team['id'], team['team_name']) for team in teams]

#     if form.validate_on_submit():
#         try:
#             con = sql.connect(current_app.config['DATABASE'])
#             cur = con.cursor()
#             cur.execute(
#                 """
#                 INSERT INTO contacts (employee_name, email_address, phone_number, team_id)
#                 VALUES (?, ?, ?, ?)
#                 """,
#                 (form.employee_name.data, form.email_address.data, form.phone_number.data, form.team_id.data)
#             )
#             con.commit()
#             flash('Team member added successfully!', category='success')

#         except Exception as e:
#             flash(f'Error occurred while adding the team member: {str(e)}', category='error')

#         finally:
#             con.close()

#         return redirect(url_for('views.see_team_members', id=team_id))  # Redirect to the team's member list page

#     return render_template('employee_table/add_employee.html', form=form, team_id=team_id)


# @employees.route("/update/<int:member_id>", methods=['GET', 'POST'])
# @login_required
# def edit_team_member(member_id):
#     con = sql.connect(current_app.config['DATABASE'])
#     con.row_factory = sql.Row
#     cur = con.cursor()
#     cur.execute("SELECT * FROM contacts WHERE id=?", (member_id,))
#     member = cur.fetchone()
#     con.close()

#     if not member:
#         flash('Team member not found!', 'danger')
#         return redirect(url_for('views.contacts'))

#     form = EditTeamMemberForm()

#     # Populate team_id select field with team options
#     con = sql.connect(current_app.config['DATABASE'])
#     con.row_factory = sql.Row
#     cur = con.cursor()
#     cur.execute("SELECT id, team_name FROM teams")
#     teams = cur.fetchall()
#     con.close()

#     form.team_id.choices = [(team['id'], team['team_name']) for team in teams]

#     if request.method == 'GET':
#         form.employee_name.data = member['employee_name']
#         form.email_address.data = member['email_address']
#         form.phone_number.data = member['phone_number']
#         form.team_id.data = member['team_id']

#     if request.method == 'POST' and form.validate_on_submit():
#         employee_name = form.employee_name.data
#         email_address = form.email_address.data
#         phone_number = form.phone_number.data
#         team_id = form.team_id.data

#         con = sql.connect(current_app.config['DATABASE'])
#         cur = con.cursor()
#         cur.execute("""
#             UPDATE contacts
#             SET employee_name = ?, email_address = ?, phone_number = ?, team_id = ?
#             WHERE id = ?
#         """, (employee_name, email_address, phone_number, team_id, member_id))
#         con.commit()
#         con.close()

#         flash('Team member updated successfully!', 'success')
#         return redirect(url_for('views.see_team_members', id=team_id))

#     return render_template('employee_table/edit_employee.html', form=form, member=member)


# @employees.route("/delete_team_member/<int:member_id>", methods=['GET'])
# @admin_required
# def delete_team_member(member_id):
#     con = sql.connect(current_app.config['DATABASE'])
#     con.row_factory = sql.Row
#     cur = con.cursor()
#     cur.execute("SELECT * FROM contacts WHERE id=?", (member_id,))
#     member = cur.fetchone()

#     # Delete the member from the database
#     con.execute("DELETE FROM contacts WHERE id=?", (member_id,))
#     con.commit()
#     con.close()

#     flash('Team member deleted successfully!', 'danger')
#     return redirect(url_for('views.see_team_members', id=member['team_id']))
