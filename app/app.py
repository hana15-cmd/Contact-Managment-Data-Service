
# from flask import Flask, flash, redirect, render_template, request, url_for
# import sqlite3 as sql

# app=Flask(__name__)

# @app.route ("/index")
# def index():
#     con=sql.connect("teamDatabase.db")
#     con.row_factory=sql.Row
#     cur=con.cursor()
#     cur.execute("select * from teams")
#     data=cur.fetchall()
#     return render_template('index.html',datas=data)

# @app.route ("/add_team",methods=['POST','GET'])
# def add_team():
#     if request.method=='POST':
#         team_name=request.form['teamName']
#         team_location=request.form['teamLocation']
#         number_of_team_members=request.form['numberOfTeamMembers']
#         team_email_address=request.form['EmailAddress']
#         team_phone_number=request.form['PhoneNumber']
#         con=sql.connect("teamDatabase.db")
#         cur=con.cursor()
#         cur.execute("INSERT INTO teams(TEAM_NAME,TEAM_LOCATION,NUMBER_OF_TEAM_MEMBERS,EMAIL_ADDRESS,PHONE_NUMBER)) values (?,?,?,?,?) ",
#                     (team_name,team_location,number_of_team_members,team_email_address,team_phone_number))
#         con.commit()
#         flash('Team added!','success')
#         return redirect(url_for("index"))
#     return render_template('add_team.html')

# @app.route("/edit_team/<string:uid>",methods=['POST','GET'])
# def edit_team(id):
#     if request.method=='POST':
#         team_name=request.form['teamName']
#         team_location=request.form['teamLocation']
#         number_of_team_members=request.form['numberOfTeamMembers']
#         team_email_address=request.form['EmailAddress']
#         team_phone_number=request.form['PhoneNumber']
#         con=sql.connect("teamDatabase.db")
#         cur=con.cursor()
#         cur.execute("update teams set TEAM_NAME=?,CONTACT=? where ID=?",(team_name,team_location,number_of_team_members,team_email_address,team_phone_number,id))
#         con.commit()
#         flash('Team Updated','success')
#         return redirect(url_for("index"))
#     con=sql.connect("teamDatabase.db")
#     con.row_factory=sql.Row
#     cur=con.cursor()
#     cur.execute("select * from teams where ID=?",(id,))
#     data=cur.fetchone()
#     return render_template("edit_team.html",datas=data)
    
# @app.route("/delete_team/<string:uid>",methods=['GET'])
# def delete_teams(id):
#     con=sql.connect("teamDatabase.db")
#     cur=con.cursor()
#     cur.execute("delete from teams where ID=?",(id))
#     con.commit()
#     flash('Team Deleted','warning')
#     return redirect(url_for("index"))
    
       
       










