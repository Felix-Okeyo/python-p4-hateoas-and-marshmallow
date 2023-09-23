#!/usr/bin/env python3

from flask import Flask, request, make_response
from flask_marshmallow import Marshmallow
from flask_migrate import Migrate
from flask_restful import Api, Resource

# Importing database-related modules and the Newsletter model
from models import db, Newsletter

# Initialize Flask app
app = Flask(__name__)

# Configure the database URI and disable modification tracking
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///newsletters.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Ensure pretty JSON output
app.json.compact = False

# Initialize database migration and attach it to the app
migrate = Migrate(app, db)
db.init_app(app)

# Initialize Marshmallow for object serialization
ma = Marshmallow(app)

# Create a schema for the Newsletter model
class NewsletterSchema(ma.SQLAlchemySchema):

    class Meta:
        model = Newsletter
        load_instance = True

    # Define fields for serialization
    title = ma.auto_field()
    published_at = ma.auto_field()

    # Define hyperlinks for RESTful URLs
    url = ma.Hyperlinks(
        {
            "self": ma.URLFor(
                "newsletterbyid",
                values=dict(id="<id>")),
            "collection": ma.URLFor("newsletters"),
        }
    )

# Create instances of the Newsletter schema for single and multiple objects
newsletter_schema = NewsletterSchema()
newsletters_schema = NewsletterSchema(many=True)

# Initialize Flask-RESTful API
api = Api(app)

# Create a resource for the root path ("/")
class Index(Resource):

    def get(self):
        # Create a response dictionary
        response_dict = {
            "index": "Welcome to the Newsletter RESTful API",
        }
        # Create a response with the dictionary and status code 200
        response = make_response(
            response_dict,
            200,
        )
        return response

# Add the Index resource to the API with the endpoint "/"
api.add_resource(Index, '/')

# Create a resource for managing newsletters ("/newsletters")
class Newsletters(Resource):

    def get(self):
        # Query all newsletters from the database
        newsletters = Newsletter.query.all()
        # Serialize the newsletters and create a response with status code 200
        response = make_response(
            newsletters_schema.dump(newsletters),
            200,
        )
        return response

    def post(self):
        # Create a new newsletter object from form data
        new_newsletter = Newsletter(
            title=request.form['title'],
            body=request.form['body'],
        )
        # Add the new newsletter to the database and commit changes
        db.session.add(new_newsletter)
        db.session.commit()
        # Serialize the new newsletter and create a response with status code 201
        response = make_response(
            newsletter_schema.dump(new_newsletter),
            201,
        )
        return response

# Add the Newsletters resource to the API with the endpoint "/newsletters"
api.add_resource(Newsletters, '/newsletters')

# Create a resource for managing a single newsletter by ID ("/newsletters/<id>")
class NewsletterByID(Resource):

    def get(self, id):
        # Query a newsletter by its ID
        newsletter = Newsletter.query.filter_by(id=id).first()
        # Serialize the newsletter and create a response with status code 200
        response = make_response(
            newsletter_schema.dump(newsletter),
            200,
        )
        return response

    def patch(self, id):
        # Query a newsletter by its ID
        newsletter = Newsletter.query.filter_by(id=id).first()
        # Update the newsletter attributes with data from the request form
        for attr in request.form:
            setattr(newsletter, attr, request.form[attr])
        # Add the updated newsletter to the database and commit changes
        db.session.add(newsletter)
        db.session.commit()
        # Serialize the updated newsletter and create a response with status code 200
        response = make_response(
            newsletter_schema.dump(newsletter),
            200
        )
        return response

    def delete(self, id):
        # Query a newsletter by its ID
        record = Newsletter.query.filter_by(id=id).first()
        # Delete the newsletter from the database and commit changes
        db.session.delete(record)
        db.session.commit()
        # Create a response dictionary
        response_dict = {"message": "record successfully deleted"}
        # Create a response with the dictionary and status code 200
        response = make_response(
            response_dict,
            200
        )
        return response

# Add the NewsletterByID resource to the API with the endpoint "/newsletters/<int:id>"
api.add_resource(NewsletterByID, '/newsletters/<int:id>')

# Start the Flask app if this script is executed
if __name__ == '__main__':
    app.run(port=5555, debug=True)
