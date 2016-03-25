import json

from sqlalchemy.orm import relationship
import sqlalchemy.types as types

from App.core import db


class JSONType(types.TypeDecorator):
    """ Very basic type to store JSON as VARCHAR """
    impl = types.VARCHAR 

    def process_bind_param(self, value, dialect):
        return json.dumps(value)

    def process_result_value(self, value, dialect):
        return json.loads(value)


class Font(db.Model):
    __tablename__ = 'fonts'

    id = db.Column('id', db.Integer(), primary_key=True)
    full_name = db.Column(db.String(255), nullable=False)
    post_script_name = db.Column(db.String(255), unique=True)
    weight = db.Column(db.Integer)
    filename = db.Column(db.String(255), nullable=False)
    copyright = db.Column(db.String(255))
    style = db.Column(db.String(255))

    name = db.Column(db.String(255), db.ForeignKey('fontmeta.name'))

    @property
    def as_dict(self):
        d = {'id':self.id,
             'full_name':self.full_name,
             'post_script_name':self.post_script_name,
             'weight':self.weight,
             'filename':self.filename,
             'copyright':self.copyright,
             'style':self.style,
             'name':self.name}
        return d

    def __repr__(self):
        return '<{}>'.format(self.post_script_name)

class Category(db.Model):
    __tablename__ = 'categories'

    id = db.Column('id', db.Integer(), primary_key=True)
    Category = db.Column('category', db.String(255), nullable=False, unique=True)
    category_rel = relationship('FontMeta', backref='category') 

    def __repr__(self):
        return '<{}>'.format(self.Category)

class FontMeta(db.Model):
    __tablename__ = 'fontmeta'

    id = db.Column('id', db.Integer(), primary_key=True)
    name = db.Column(db.String(255), nullable=False, unique=True)
    designer = db.Column(db.String(255)) ## there should be a link to designer info somewhere
    license = db.Column(db.String(255)) ## there should be a link to license text somewhere
    date_added = db.Column(db.Date)

    category_ref = db.Column('category', 
                             db.String(255), 
                             db.ForeignKey('categories.category'), 
                             nullable=False)

    font_id = db.Column(db.Integer(), db.ForeignKey('fonts.id'))

    fonts = db.relationship('Font', 
                            # foreign_keys=[font_id], 
                            primaryjoin='Font.name==FontMeta.name',
                            uselist=True,
                            single_parent=True,
                            cascade="all, delete-orphan",
                            order_by='Font.post_script_name')

    subsets = db.Column(JSONType(255))

    @property
    def as_dict(self):
        d = {'id':self.id,
             'name':self.name,
             'designer':self.designer,
             'license':self.license,
             'date_added': self.date_added.strftime('%d/%m/%Y'),
             'category':self.category_ref,
             'fonts':[i.as_dict for i in self.fonts],
             'subsets':self.subsets}
        return d

    def __repr__(self):
        return '<{}[{}]>'.format(self.name, self.category)
