from exts import db
import datetime

class Mydata(db.Model):
    __tablename__ = "mydata"
    id = db.Column(db.Integer,primary_key=True,autoincrement=True)
    content = db.Column(db.Text, nullable=False)
    create_time = db.Column(db.DateTime, default=datetime.datetime.now)
    photo_path=db.Column(db.String(50),nullable=True)
    flag=db.Column(db.Boolean,nullable=True)
    def __repr__(self):
        return repr({"id":self.id,"content":self.content,"photo_path":self.photo_path,"create_time":self.create_time,"flag":self.flag})