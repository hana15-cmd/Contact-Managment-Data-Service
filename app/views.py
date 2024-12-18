from flask import Blueprint, render_template, request, redirect, url_for, session, flash, current_app
from flask_login import login_required
from app.forms import AddTeamForm, AddTeamMemberForm, EditTeamForm
from app.database_logic.models import add_dummy_contacts_data, add_entry, admin_required, get_database
import sqlite3 as sql
from .forms import EditTeamMemberForm

views = Blueprint( 'views', __name__ )

@views.route( '/' )
def home():
    return render_template( "homepage.html" )

@views.route( '/init_db' )
def initialize_db():
    try:
        from app.database_logic.models import init_db_scheme, add_dummy_teams_data, add_dummy_contacts_data

        init_db_scheme()  # Set up the database schema
        add_dummy_teams_data()  # Populate with dummy teams data
        add_dummy_contacts_data()  # Populate with dummy contacts data

        flash( 'Database initialized successfully with dummy data!', 'success' )
        return redirect( url_for( 'views.home' ) )
    except Exception as e:
        flash( f'Error during database initialization: {str( e )}', 'danger' )
        return redirect( url_for( 'views.home' ) )


@views.route( '/contactManager', methods=['GET', 'POST'] )
def contacts():
    # Get search and filter query parameters from the URL (default to empty if not provided)
    search_query = request.args.get( 'search', '' )  # Get the search query from the URL
    filter_column = request.args.get( 'filter', '' )  # Get the filter column (optional)

    # Establish database connection
    database = get_database()
    cursor = database.cursor()

    # Start with the base SQL query
    sql_query = """
    SELECT 
        t.ID, 
        t.TEAM_NAME, 
        t.TEAM_LOCATION, 
        t.EMAIL_ADDRESS, 
        (SELECT COUNT(*) FROM contacts c WHERE c.team_id = t.ID) AS NUMBER_OF_TEAM_MEMBERS
    FROM teams t
    """
    sql_params = []

    # Modify the query based on user input
    if search_query:
        # If both search query and filter column are provided
        if filter_column:
            sql_query += f" WHERE {filter_column} LIKE ?"
            sql_params.append( f"%{search_query}%" )
        else:
            # If no filter column is specified, search across multiple columns
            sql_query += """
                WHERE TEAM_NAME LIKE ? 
                OR TEAM_LOCATION LIKE ? 
                OR EMAIL_ADDRESS LIKE ?
            """
            sql_params.extend( [f"%{search_query}%", f"%{search_query}%", f"%{search_query}%"] )

    cursor.execute( sql_query, sql_params )
    data = cursor.fetchall()

    # Return the template with the filtered data and search information
    return render_template( "index.html", datas=data, search_query=search_query, filter_column=filter_column )


@views.route( "/add_team", methods=['POST', 'GET'] )
@login_required
def add_team():
    form = AddTeamForm()

    if form.validate_on_submit():
        team_name = form.team_name.data
        team_location = form.team_location.data
        number_of_team_members = form.number_of_team_members.data
        team_email_address = form.team_email_address.data

        try:
            con = sql.connect( current_app.config['DATABASE'] )
            cur = con.cursor()

            # Insert data into the database
            cur.execute(
                """
                INSERT INTO teams (TEAM_NAME, TEAM_LOCATION, NUMBER_OF_TEAM_MEMBERS, EMAIL_ADDRESS)
                VALUES (?, ?, ?, ?)
                """,
                (team_name, team_location, number_of_team_members, team_email_address)
            )
            con.commit()

            flash( 'Team added successfully!', category='success' )
            return redirect( url_for( "views.contacts" ) )

        except Exception as e:
            flash( f'Error occurred while adding the team: {str( e )}', category='error' )
        finally:
            con.close()

    return render_template( 'team_table/add_team.html', form=form )


@views.route("/edit_team/<string:id>", methods=['POST', 'GET'])
@login_required
def edit_team(id):
    # Initialise the connection to the database
    con = sql.connect(current_app.config['DATABASE'])
    con.row_factory = sql.Row
    cur = con.cursor()

    # Fetch the team data for the specified ID
    cur.execute("SELECT * FROM teams WHERE ID=?", (id,))
    data = cur.fetchone()

    if not data:
        flash("Team not found!", "danger")
        return redirect(url_for("views.contacts"))

    form = EditTeamForm()
    form.set_team_id(id)

    # Recalculate the number of members for the team
    cur.execute("SELECT COUNT(*) FROM contacts WHERE team_id=?", (id,))
    number_of_members = cur.fetchone()[0]

    # Pre-fill the form with existing team data (GET request)
    if request.method == 'GET':
        form.team_name.data = data['TEAM_NAME']
        form.team_location.data = data['TEAM_LOCATION']
        form.number_of_team_members.data = number_of_members  # Set dynamic count
        form.team_email_address.data = data['EMAIL_ADDRESS']

    # Handle form submission (POST request)
    if request.method == 'POST' and form.validate_on_submit():
        team_name = form.team_name.data
        team_location = form.team_location.data
        team_email_address = form.team_email_address.data

        try:
            # Recalculate the number of members again (POST request)
            cur.execute("SELECT COUNT(*) FROM contacts WHERE team_id=?", (id,))
            number_of_members = cur.fetchone()[0]

            # Update the team data in the database
            cur.execute("""
                UPDATE teams
                SET TEAM_NAME=?, TEAM_LOCATION=?, NUMBER_OF_TEAM_MEMBERS=?, EMAIL_ADDRESS=?
                WHERE ID=?
            """, (team_name, team_location, number_of_members, team_email_address, id))

            con.commit()

            flash('Team Updated Successfully', 'success')
            return redirect(url_for("views.contacts"))
        except Exception as e:
            flash(f"An error occurred while updating the team: {e}", 'danger')
        finally:
            con.close()

    return render_template('team_table/edit_team.html', form=form, datas=data)


@views.route( "/delete_team/<string:id>", methods=['GET'] )
@admin_required
def delete_team(id):
    try:
        con = sql.connect( current_app.config['DATABASE'] )
        cur = con.cursor()
        cur.execute( "DELETE FROM teams WHERE ID=?", (id,) )
        con.commit()
        flash( 'Team deleted successfully!', 'warning' )
    except Exception as e:
        flash( f"An error occurred while deleting the team: {str( e )}", 'danger' )
    finally:
        con.close()

    return redirect( url_for( "views.contacts" ) )


@views.route( "/see_team_members/<string:id>", methods=['POST', 'GET'] )
@login_required
def see_team_members(id):
    # Validate the ID
    if not id.isdigit():
        flash( "Invalid team ID.", "danger" )
        return redirect( url_for( "views.contacts" ) )

    con = sql.connect( current_app.config['DATABASE'] )
    con.row_factory = sql.Row
    try:
        cur = con.cursor()

        # Fetch team details
        cur.execute( "SELECT * FROM teams WHERE ID=?", (id,) )
        team = cur.fetchone()

        if not team:
            flash( f"No team found with ID {id}.", "danger" )
            return redirect( url_for( "views.contacts" ) )

        # Fetch team members
        cur.execute( "SELECT * FROM contacts WHERE team_id=?", (id,) )
        members = cur.fetchall()

        if not members:
            flash( "No members found for this team. Adding dummy members for testing.", "info" )

            # Call the add_dummy_contacts_data function to insert dummy data
            add_dummy_contacts_data()

            # Refresh the members list after inserting dummy data
            cur.execute( "SELECT * FROM contacts WHERE team_id=?", (id,) )
            members = cur.fetchall()

        # Render the template with team and member details
        return render_template( "employee_table/team_member_info.html", team=team, members=members )
    except Exception as e:
        flash( "An unexpected error occurred. Please try again later.", "danger" )
        return redirect( url_for( "views.contacts" ) )
    finally:
        if con:
            con.close()

 # This is the second table routings 
@views.route( "/add_team_member/<int:team_id>", methods=['POST', 'GET'] )
@login_required
def add_team_member(team_id):
    form = AddTeamMemberForm()

    # Fetch teams to populate the select field
    con = sql.connect( current_app.config['DATABASE'] )
    con.row_factory = sql.Row
    cur = con.cursor()
    cur.execute( "SELECT id, team_name FROM teams" )
    teams = cur.fetchall()
    con.close()

    # Populate the team select field choices
    form.team_id.choices = [(team['id'], team['team_name']) for team in teams]

    if form.validate_on_submit():
        try:
            con = sql.connect( current_app.config['DATABASE'] )
            cur = con.cursor()
            cur.execute(
                """
                INSERT INTO contacts (employee_name, email_address, phone_number, team_id)
                VALUES (?, ?, ?, ?)
                """,
                (form.employee_name.data, form.email_address.data, form.phone_number.data, form.team_id.data)
            )
            con.commit()
            flash( 'Team member added successfully!', category='success' )

        except Exception as e:
            flash( f'Error occurred while adding the team member: {str( e )}', category='error' )

        finally:
            con.close()

        return redirect( url_for( 'views.see_team_members', id=team_id ) )  # Redirect to the team's member list page

    return render_template( 'employee_table/add_employee.html', form=form, team_id=team_id )


@views.route( "/edit_team_member/<int:member_id>", methods=['GET', 'POST'] )
@login_required
def edit_team_member(member_id):
    con = sql.connect( current_app.config['DATABASE'] )
    con.row_factory = sql.Row
    cur = con.cursor()
    cur.execute( "SELECT * FROM contacts WHERE id=?", (member_id,) )
    member = cur.fetchone()
    con.close()

    if not member:
        flash( 'Team member not found!', 'danger' )
        return redirect( url_for( 'views.contacts' ) )

    form = EditTeamMemberForm()

    # Populate team_id select field with team options
    con = sql.connect( current_app.config['DATABASE'] )
    con.row_factory = sql.Row
    cur = con.cursor()
    cur.execute( "SELECT id, team_name FROM teams" )
    teams = cur.fetchall()
    con.close()

    form.team_id.choices = [(team['id'], team['team_name']) for team in teams]

    if request.method == 'GET':
        form.employee_name.data = member['employee_name']
        form.email_address.data = member['email_address']
        form.phone_number.data = member['phone_number']
        form.team_id.data = member['team_id']

    if request.method == 'POST' and form.validate_on_submit():
        employee_name = form.employee_name.data
        email_address = form.email_address.data
        phone_number = form.phone_number.data
        team_id = form.team_id.data

        con = sql.connect( current_app.config['DATABASE'] )
        cur = con.cursor()
        cur.execute( """
            UPDATE contacts
            SET employee_name = ?, email_address = ?, phone_number = ?, team_id = ?
            WHERE id = ?
        """, (employee_name, email_address, phone_number, team_id, member_id) )
        con.commit()
        con.close()

        flash( 'Team member updated successfully!', 'success' )
        return redirect( url_for( 'views.see_team_members', id=team_id ) )

    return render_template( 'employee_table/edit_employee.html', form=form, member=member )


@views.route( "/delete_team_member/<int:member_id>", methods=['GET'] )
@admin_required
def delete_team_member(member_id):
    con = sql.connect( current_app.config['DATABASE'] )
    con.row_factory = sql.Row
    cur = con.cursor()
    cur.execute( "SELECT * FROM contacts WHERE id=?", (member_id,) )
    member = cur.fetchone()

    # Delete the member from the database
    con.execute( "DELETE FROM contacts WHERE id=?", (member_id,) )
    con.commit()
    con.close()

    flash( 'Team member deleted successfully!', 'danger' )
    return redirect( url_for( 'views.see_team_members', id=member['team_id'] ) )
