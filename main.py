from flask import Flask, render_template, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from flask_wtf.form import _Auto
from wtforms import SubmitField, StringField, IntegerField, SelectField, SelectMultipleField, widgets, HiddenField
from wtforms.validators import DataRequired
import os
import datetime

basedir = os.path.abspath(os.path.dirname(__file__))

app = Flask(__name__)
app.config["SECRET_KEY"] = "hard to guess string"
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///" + os.path.join(basedir, "data.sqlite")
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False


db = SQLAlchemy(app)


class SupplierForm(FlaskForm):
    name = StringField('Supplier Name: ')
    phone_no = StringField('Phone No. ')
    email = StringField('Email')
    submit = SubmitField('Submit')


class IngredientForm(FlaskForm):
    name = StringField('Ingredient Name:')
    measurement = StringField('Measurement: ')
    unit_cost = IntegerField('Unit Cost')
    submit = SubmitField('Submit')


class MultiCheckboxField(SelectMultipleField):
    widget = widgets.ListWidget(prefix_label=False)
    option_widget = widgets.CheckboxInput()


class SupplierIngredientForm(FlaskForm):
    supplier = SelectField('Supplier', coerce=int, validators=[DataRequired()])
    ingredients = MultiCheckboxField('Ingredients', coerce=int)
    submit = SubmitField('Submit')

    def __init__(self, *args, **kwargs):
        super(SupplierIngredientForm, self).__init__(*args, **kwargs)

        self.supplier.choices = [(supplier.id, supplier.name)
                                 for supplier in Supplier.query.order_by(Supplier.name).all()]
        
        self.ingredients.choices = [(ingredient.id, ingredient.name) 
                                    for ingredient in Ingredient.query.all()]


class SupplierIngredient(db.Model):
    __tablename__ = "supplier_ingredients"

    supplier_id = db.Column(db.Integer, db.ForeignKey('suppliers.id'), primary_key=True)
    ingredient_id = db.Column(db.Integer, db.ForeignKey('ingredients.id'), primary_key=True)

    supplier = db.relationship('Supplier', backref=db.backref('supplier_ingredients', cascade='all, delete-orphan'))
    ingredient = db.relationship('Ingredient', backref=db.backref('supplier_ingredients', cascade='all, delete-orphan'))


class Supplier(db.Model):
    __tablename__ = "suppliers"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)
    phone_no = db.Column(db.String(13), nullable=False)
    email = db.Column(db.String(50))
    created_at = db.Column(db.DateTime(), default=datetime.datetime.utcnow())
    updated_at = db.Column(db.DateTime(), default=datetime.datetime.utcnow())


class Ingredient(db.Model):
    __tablename__ = "ingredients"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)
    unit_of_measurement = db.Column(db.String(12))
    unit_cost = db.Column(db.Integer)
    created_at = db.Column(db.DateTime(), default=datetime.datetime.utcnow())
    updated_at = db.Column(db.DateTime(), default=datetime.datetime.utcnow())




@app.route("/")
def index():
    # fetch and display all ingredients
    ingredients = Ingredient.query.all()
    # fetch and display all suppliers
    suppliers = Supplier.query.all()
    return render_template("index.html", ingredients=ingredients, suppliers=suppliers)

@app.route("/add_ingredient", methods=["GET", "POST"])
def add_ingredient():
    form = IngredientForm()
    if form.validate_on_submit():
        ingredient = Ingredient(
            name=form.name.data, 
            unit_of_measurement=form.measurement.data,
            unit_cost=form.unit_cost.data
            )
        db.session.add(ingredient)
        db.session.commit()
        flash("Ingredient added successfully.")
        return redirect(url_for("index"))
    return render_template("add_ingredient.html", form=form)

@app.route("/add_supplier", methods=["GET", "POST"])
def add_supplier():
    form = SupplierForm()
    if form.validate_on_submit():
        supplier = Supplier(
            name=form.name.data, 
            phone_no=form.phone_no.data, 
            email=form.email.data
            )
        db.session.add(supplier)
        db.session.commit()
        flash("Supplier added successfully")
        return redirect(url_for('index'))
    return render_template("add_supplier.html", form=form)

@app.route("/add_supplier_ingredient", methods=["GET", "POST"])
def add_supplier_ingredient():
    form = SupplierIngredientForm()
    if form.validate_on_submit():
        supplier_id = form.supplier.data
        ingredients = Ingredient.query.all()
        selected_ingredients = []
        for ingredient in ingredients:
            if ingredient.id in form.ingredients.data:
                selected_ingredients.append(ingredient)
                supplier_ingredient = SupplierIngredient(
                    supplier_id=supplier_id, 
                    ingredient_id=ingredient.id
                    )
                db.session.add(supplier_ingredient)
        db.session.commit()
        flash('Supplier Ingredient added successfully')
        return redirect(url_for('index'))
    return render_template('supplier_ingredient.html', form=form)
            

if __name__ == "__main__":
    app.run(debug=True)
