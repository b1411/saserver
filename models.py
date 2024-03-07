from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), nullable=False)
    phone = db.Column(db.String(20), nullable=False)
    studyPlan = db.Column(db.String(100), nullable=False)
    studyProgram = db.Column(db.String(100), nullable=False)
    factors = db.Column(db.String(1000), nullable=False)
    campus = db.Column(db.String(100), nullable=False)
    photo = db.Column(db.String(200), nullable=False)
    processed_photo = db.Column(db.String(200), nullable=False)
    rembg = db.Column(db.Boolean, nullable=False)

    def __repr__(self): 
        return f'<User {self.name}>'

