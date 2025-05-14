import os
from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  # Allow cross-origin requests

# PostgreSQL connection URI
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# Book Model
class Book(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    genre = db.Column(db.String(50))
    pages = db.Column(db.Integer)  # Added pages attribute
    author_id = db.Column(db.Integer, db.ForeignKey('author.id'), nullable=False)
    author = db.relationship('Author', backref=db.backref('books', lazy=True))

    def __repr__(self):
        return f'<Book {self.title}>'

# Author Model
class Author(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)

    def __repr__(self):
        return f'<Author {self.name}>'

    @property
    def book_count(self):
        # Property that returns the number of books written by the author
        return len(self.books)

# Route to get all books
@app.route('/books', methods=['GET'])
def get_books():
    books = Book.query.all()
    return jsonify([{
        'id': book.id,
        'title': book.title,
        'genre': book.genre,
        'pages': book.pages,
        'author': book.author.name
    } for book in books])

# Route to add a new book
@app.route('/books', methods=['POST'])
def add_book():
    data = request.get_json()
    author = Author.query.get_or_404(data['author_id'])
    new_book = Book(
        title=data['title'],
        genre=data['genre'],
        pages=data['pages'],
        author_id=data['author_id']
    )
    db.session.add(new_book)
    db.session.commit()
    return jsonify({'message': 'Book added successfully'}), 201

# Route to update book details
@app.route('/books/<int:id>', methods=['PUT'])
def update_book(id):
    book = Book.query.get_or_404(id)
    data = request.get_json()
    book.title = data['title']
    book.genre = data['genre']
    book.pages = data['pages']
    book.author_id = data['author_id']
    db.session.commit()
    return jsonify({'message': 'Book updated successfully'})

# Route to delete a book
@app.route('/books/<int:id>', methods=['DELETE'])
def delete_book(id):
    book = Book.query.get_or_404(id)
    db.session.delete(book)
    db.session.commit()
    return jsonify({'message': 'Book deleted successfully'})

# Route to get all authors
@app.route('/authors', methods=['GET'])
def get_authors():
    authors = Author.query.all()
    return jsonify([{
        'id': author.id,
        'name': author.name,
        'book_count': author.book_count  # Show the number of books by the author
    } for author in authors])

# Route to add a new author
@app.route('/authors', methods=['POST'])
def add_author():
    data = request.get_json()
    new_author = Author(name=data['name'])
    db.session.add(new_author)
    db.session.commit()
    return jsonify({'message': 'Author added successfully'}), 201

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
