from flask_login import UserMixin
from deta import Deta
import bcrypt
from dotenv import get_key
import ssl
from flask import request

ssl._create_default_https_context = ssl._create_unverified_context


class User(UserMixin):
   def __init__(self, user_dict):
      self.user_dict = user_dict

   def get_id(self):
      user_mail = self.user_dict['key']
      return user_mail

   def is_authenticated(self):
       project_key = get_key(key_to_get="Project_Key", dotenv_path=".env")
       deta = Deta(project_key=project_key)
       req_header = str(request.headers).split('/')[-1]
       if req_header == 'login':
            user_database = deta.Base('login_data')
       elif req_header =='adminlogin':
            user_database = deta.Base('admin_data')
       try:
           user_password=str(user_password)
           user_password=user_password.encode('utf-8')
           try:
               query = user_database.fetch(query={'key':self.user_dict['key']}).items[0]
               hashed_password = query['Password'].encode('utf-8')
               if bcrypt.checkpw(user_password,hashed_password):
                   return True
               else:
                   return False
           except IndexError as ie:
               if IndexError:
                   print(ie)
                   return False
       except Exception as e:
           print(e)
           print("not found")
           return False