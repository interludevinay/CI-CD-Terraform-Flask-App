from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
import os

app = Flask(__name__)

# Database config (SQLite inside "instance" folder)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///todo.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Task Model
class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    content = db.Column(db.Text, nullable=True)

    def __repr__(self):
        return f'<Task {self.id} - {self.title}>'

# Routes
@app.route('/')
def index():
    tasks = Task.query.all()
    return render_template('index.html', tasks=tasks)

@app.route('/add', methods=['GET', 'POST'])
def add():
    if request.method == 'POST':
        title = request.form['title']
        content = request.form.get('content')
        new_task = Task(title=title, content=content)
        db.session.add(new_task)
        db.session.commit()
        return redirect(url_for('index'))
    return render_template('add.html')

@app.route('/edit/<int:id>', methods=['GET', 'POST'])
def edit(id):
    task = Task.query.get_or_404(id)
    if request.method == 'POST':
        task.title = request.form['title']
        task.content = request.form.get('content')
        db.session.commit()
        return redirect(url_for('index'))
    return render_template('edit.html', task=task)

@app.route('/delete/<int:id>')
def delete(id):
    task = Task.query.get_or_404(id)
    db.session.delete(task)
    db.session.commit()
    return redirect(url_for('index'))

# Run App
if __name__ == '__main__':
    # Ensure "instance" folder exists
    if not os.path.exists('instance'):
        os.makedirs('instance')

    # Create DB tables if not exist
    with app.app_context():
        db.create_all()

    app.run(debug=True)
