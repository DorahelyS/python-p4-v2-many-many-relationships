'''
Introduction
In the previous lesson, we saw how to create a one-to-many relationship by assigning the correct foreign key on our tables, and using the relationship() method along with the back_populates() parameter.

In the SQL modules, we learned about one other kind of relationship: the many-to-many, also known as the has many through, relationship. For instance, in a domain where a cat has many owners and an owner has many cats, we need to create a table named cat_owners with foreign keys to the two related tables:

In this lesson, we'll learn different ways to implement many-to-many relationships for a data model containing employees, meetings, projects , and assignments:

An employee has many meetings.
A meeting has many employees.
An employee has many projects through assignments.
A project has many employees through assignments.
An assignment belongs to an employee.
An assignment belongs to a project.

Setup
This lesson is a code-along, so fork and clone the repo.

Run pipenv install to install the dependencies and pipenv shell to enter your virtual environment before running your code.

 pipenv install
 pipenv shell
Change into the server directory and configure the FLASK_APP and FLASK_RUN_PORT environment variables:

 cd server
 export FLASK_APP=app.py
 export FLASK_RUN_PORT=5555
The file server/models.py defines models named Employee, Meeting, and Project. Relationships have not been established between the models.

Run the following commands to create and seed the tables with sample data.

 flask db init
 flask db migrate -m "initial migration"
 flask db upgrade head
 python seed.py

Many-To-Many with Table Objects
Many-to-many relationships in SQLAlchemy use intermediaries called association tables (also called join tables). These are tables that exist only to join two related tables together.

There are two approaches to building these associations: association objects, which are most similar to the models we've built so far, and the more common approach, Table objects.

We'll implement the many-to-many between employees and meetings by creating a table named employee_meetings. Since employee_meetings is on the many side of its relationships with employees and meetings, the table will store two foreign keys employee_id and meeting_id to reference the primary keys of the other two tables.

Update models.py to add the new association table employee_meetings as shown below. NOTE: You'll need to place this above the Employee and Meeting models within models.py so they may reference it.

# Association table to store many-to-many relationship between employees and meetings
employee_meetings = db.Table(
    'employees_meetings',
    metadata,
    db.Column('employee_id', db.Integer, db.ForeignKey(
        'employees.id'), primary_key=True),
    db.Column('meeting_id', db.Integer, db.ForeignKey(
        'meetings.id'), primary_key=True)
)

You'll need to migrate the schema with the new table:

flask db migrate -m 'add employee_meetings association table'
flask db upgrade head
Update seed.py to import the table data structure:

from models import db, Employee, Meeting, Project, employee_meetings

Update seed.py to delete the new table along with the other tables. Since the table is not created from a model class, you'll need to delete it using db.session.query(employee_meetings).delete():

# Delete all rows in tables
    db.session.query(employee_meetings).delete()
    db.session.commit()
    Employee.query.delete()
    Meeting.query.delete()
    Project.query.delete()
Update seed.py to add two meetings to an employee and to add three more employees to a meeting.

    # Many-to-many relationship between employee and meeting

    # Add meetings to an employee
    e1.meetings.append(m1)
    e1.meetings.append(m2)
    # Add employees to a meeting
    m2.employees.append(e2)
    m2.employees.append(e3)
    m2.employees.append(e4)
    db.session.commit()
Re-seed the database:

 python seed.py
Let's confirm the database table has the correct rows:

Many-To-Many with Association Objects
An employee is assigned to work on many projects, and a project may have many employees assigned to it. The database needs to keep track of the employee's role on the project, along with the dates they start and end working on the project. We'll use an association object to capture the relationship between an employee and a project, along with the attributes (role, start_date, end_date) that are specific to the assignment.

An association object is really just another model, thus the many-to-many relationship between Employee and Project is implemented as two one-to-many relationships through Assignment:

One-to-many relationship between Employee and Assignment
One-to-many relationship between Project and Assignment
Edit models.py to add a new model named Assignment having the columns and relationships as shown:

# Association Model to store many-to-many relationship between employee and project
class Assignment(db.Model):
    __tablename__ = 'assignments'

    id = db.Column(db.Integer, primary_key=True)
    role = db.Column(db.String)
    start_date = db.Column(db.DateTime)
    end_date = db.Column(db.DateTime)

    # Foreign key to store the employee id
    employee_id = db.Column(db.Integer, db.ForeignKey('employees.id'))
    # Foreign key to store the project id
    project_id = db.Column(db.Integer, db.ForeignKey('projects.id'))

    # Relationship mapping the assignment to related employee
    employee = db.relationship('Employee', back_populates='assignments')
    # Relationship mapping the assignment to related project
    project = db.relationship('Project', back_populates='assignments')

    def __repr__(self):
        return f'<Assignment {self.id}, {self.role}, {self.start_date}, {self.end_date}, {self.employee.na

The Employee and Project classes must be updated to add the relationship through Assignment. We don't use the secondary parameter since the relationship is implemented directly with the Assignment model rather than an association table.

class Employee(db.Model):
    __tablename__ = 'employees'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    hire_date = db.Column(db.Date)

    # Relationship mapping the employee to related meetings
    meetings = db.relationship(
        'Meeting', secondary=employee_meetings, back_populates='employees')

    # Relationship mapping the employee to related assignments
    assignments = db.relationship(
        'Assignment', back_populates='employee', cascade='all, delete-orphan')

    def __repr__(self):
        return f'<Employee {self.id}, {self.name}, {self.hire_date}>'

class Project(db.Model):
    __tablename__ = 'projects'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String)
    budget = db.Column(db.Integer)

    # Relationship mapping the project to related assignments
    assignments = db.relationship('Assignment', back_populates='project',cascade='all, delete-orphan')

    def __repr__(self):
        return f'<Review {self.id}, {self.title}, {self.budget}>'

Migrate the schema to reflect the new model:

flask db migrate -m 'add assignment association table'
flask db upgrade head
Update seed.py to import the new model:

from models import db, Employee, Meeting, Project, Assignment, employee_meetings
Update seed.py to delete the new table:

# Delete all rows in tables
db.session.query(employee_meetings).delete()
db.session.commit()
Employee.query.delete()
Meeting.query.delete()
Project.query.delete()
Assignment.query.delete()

You'll also need to edit seed.py to assign employees to projects. This should go at the end of the file after the employees and projects have been created.

# Many-to-many relationship between employee and project through assignment

a1 = Assignment(role='Project manager',
                start_date=datetime.datetime(2023, 5, 28),
                end_date=datetime.datetime(2023, 10, 30),
                employee=e1,
                project=p1)
a2 = Assignment(role='Flask programmer',
                start_date=datetime.datetime(2023, 6, 10),
                end_date=datetime.datetime(2023, 10, 1),
                employee=e2,
                project=p1)
a3 = Assignment(role='Flask programmer',
                start_date=datetime.datetime(2023, 11, 1),
                end_date=datetime.datetime(2024, 2, 1),
                employee=e2,
                project=p2)

db.session.add_all([a1, a2, a3])
db.session.commit()
Re-seed the database:

 python seed.py
Let's check the assignments table to confirm the 3 new rows:



'''