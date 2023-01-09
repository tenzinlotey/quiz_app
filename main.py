from flask import Flask, render_template,request,redirect,url_for,flash,session
from flask_login import login_user,login_required,LoginManager,logout_user
from password_hash.User import User
import password_hash.password_verify  as pv
import os
from dotenv import get_key,load_dotenv
from deta import Deta
import ssl
import pandas as pd
import numpy as np
import random

ssl._create_default_https_context = ssl._create_unverified_context

load_dotenv()

user_mail=""
score = 0
lscore=None
flag = True
r_list = [i for i in range(25)]
r_id=0
g_id=1
app = Flask(__name__)

app.jinja_env.filters['zip'] = zip

app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view='home'

@login_manager.user_loader
def load_user(user_mail):
   user = User(pv.User_logged)
   return user


@app.route('/')
def home():
   return render_template('index.html')



@app.route('/logout')
@login_required
def logout():
   logout_user()
   return redirect('/')


@app.route('/login',methods=['POST','GET'])
def ur():
   global user_mail
   import password_hash.password_to_hash as ps
   
   # import password_hash.password_verify as pv

   project_key =get_key(key_to_get="Project_Key",dotenv_path=".env")
   # Logging into Deta:
   deta = Deta(project_key=project_key)
   database=deta.Base("login_data")
   
   if request.method=="POST":
      submit_btn = list(request.form)[::-1]

# Sign IN:
      if submit_btn[0]=='sign-in':
         global user_mail
         # print('sign-in')
         user_mail=request.form["email"]
         user_pas=request.form['password']
         verification_msg=pv.password_verify(user_name=user_mail,user_password=user_pas)
         # print(verification_msg)
         if verification_msg=='User Verified':
            user = User(pv.User_logged)
            print(user)
            global lscore
            lscore=pv.lsc
            print(lscore)
            login_user(user,remember=True)
            return redirect('/quiz-start')
         elif verification_msg=='Incorrect Password':
            flash(message=verification_msg,category='Error')
            # return redirect('/login')
         elif verification_msg=='No Data Found, Create Account':
            flash(message=verification_msg,category='Error')
            # return redirect('/login')

         # return verification_msg

# Sign Up:
      elif submit_btn[0]=='sign-up':
         # print('sign-up')
         user_name=request.form["name"]
         user_mail=request.form["email"]
         user_pas1=request.form['password1']
         user_pas2=request.form['password2']

         if user_pas1==user_pas2:
            hash=ps.text_hash(user_pas2)
            hash=hash.decode()
            try:
               database.insert({'key':user_mail,'Name':user_name,'Password':hash,'score':[0,0,0,0,0,0,0,0,0,0]})
               msg='Registration Successfull'
               flash(message=msg,category='Success')
               return redirect('/login')

            except Exception as e:
               if 'Conflict' in str(e):
                  msg='User Already Exists, Sign In'
                  flash(message=msg,category='Error')
                  return redirect('/login')
         else:
            msg="Password Doesn't Match"
            flash(message=msg,category='Error')
            # return redirect('/login')


   return render_template('login.html')


@app.route('/adminlogin',methods=['POST','GET'])
def al():
   print("Inside adminlogin route")
   import password_hash.password_verify as pv

   print("Request data:",request.method)
   if request.method=="POST":
      print("Inside post method")
      submit_btn = list(request.form)
      print("Submit-btn")
      print("Data inside submit_btn")

      for val in submit_btn:
         print(val)

# Admin sign_in 
      print(submit_btn)
      if submit_btn[2]=='sign-in':
         # print('sign-in')
         admin_mail=request.form["email"]
         admin_pas=request.form['password']
    
         
         verification_msg=pv.password_verify1(admin_name=admin_mail,admin_password=admin_pas)
         # print(verification_msg)
         if verification_msg=='User Verified':
            print("sh")
            user = pv.User_logged
            print(user)
            login_user(User(user),remember=True)
            return redirect('/admin_dashboard')
         elif verification_msg=='Incorrect Password':
            flash(message=verification_msg,category='Error')

         elif verification_msg=='No Data Found, Invalid credentials':
            flash(message=verification_msg,category='Error')
   return render_template('adminlogin.html')




@app.route('/quiz-start')
@app.route('/quiz-start/')
@login_required
def quiz():
   return render_template('quizhome.html',sc=lscore)  


# @app.route('/quiz-start/', defaults={'id': 0})
@app.route('/quiz-start/<int:id>/<int:qno>',methods=['GET','POST'])
@login_required
def questions(id,qno):
   global r_id
   global score
   global flag
   

   user_answer = {'0':'A','1':'B','2':'C','3':'D'}
   data = pd.read_excel('./ques_set_cleaned.xlsx')

   data.index = np.arange(1,len(data)+1)

   q_id = data.at[qno,'Q.ID']
   print("Q.Id:",q_id)

   question = data.at[qno,'Questions']
   options = data.at[qno,'Options']
   options = options.split('\n')
   Answer = data.at[qno,'Answers']
   qset = (q_id,question,options,Answer)

   
   if request.method=='POST':
      try:
         selected_option = request.form.get('opt')
         print("type of selected_opt:",type(selected_option))
         print("User selected:",selected_option,"Correct ans:",Answer)
         for ele in Answer.split():
            print(ele)
         if user_answer[selected_option] == Answer.split()[-1]:
            score = score + 10

         # print("Score:",score)
         


         next_btn = request.form['next']
         # print("next button:",next_btn)
         # print("intial id:",id)
         r_id=r_id+1
         
         if r_id >24  :
            r_id=0
            global g_id
            lscore[(g_id//25)]=score
            print(lscore,g_id)
            return redirect("/score")
         # print("Value of id:",id+r_list[r_id]) 
         return redirect(f'/quiz-start/{id}/{id+r_list[r_id]}')
         # else:
         #    return redirect('/score')
            

      except Exception as e:
         print("Exception in next button",e)      
   
   return render_template('set1.html',qset = qset)
 
@app.route('/quiz-start1/<int:id>/<int:qno>',methods=['GET','POST'])
@login_required
def s_home(id,qno):
   global r_list
   global score
   global g_id
   g_id=id 
   score=0
   random.shuffle(r_list)
   return redirect(f'/quiz-start/{id}/{id+r_list[qno]}')


@app.route('/set/<id>',methods=['GET','POST'])
@login_required
def quiz1():
   # print("i'm not here")
   id=1
   return redirect(url_for('quiz-start', id=(id)))

@app.route('/score')
@app.route('/score/')
@login_required
def score1():
   #ssl._create_default_https_context = ssl._create_unverified_context
   global user_mail
   project_key =get_key(key_to_get="Project_Key",dotenv_path=".env")
   deta=Deta(project_key=project_key)
   database=deta.Base('login_data')
   database.update(key=user_mail, updates={'score':lscore})
   print(user_mail)
   return render_template('score.html',sc=score,s_id=g_id+25)

@app.route('/admin_dashboard')
@app.route('/admin_dashboard/')
@login_required
def dashboard():
   if pv.User_logged['key']!= 'admin@gmail.com':
      return redirect('\quiz-start')
   
   try:
      ssl._create_default_https_context = ssl._create_unverified_context
      project_key =get_key(key_to_get="Project_Key",dotenv_path=".env")
   # Logging into Deta:
      deta = Deta(project_key=project_key)
      database=deta.Base("login_data")
      query = database.fetch().items
      # data = [query[i].pop('Password') for i in range(len(query))]
      # print(data)
      print(query[0]['Password'])
      df = pd.DataFrame(query)
      df = df[['key','Name','score']]
      df.rename(columns={'key':'Email'},inplace=True)
      # print(df)
      # df_table = df.to_html()
      df_table = df.to_dict()

   except Exception as e:
      print(e)
      print('data not available')
   
   return render_template('admin_dashboard.html',q=df_table,zip = zip)


if __name__ == '__main__':
   app.run(debug=True,port=4000)

