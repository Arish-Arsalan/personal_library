import streamlit as st
import psycopg2
from psycopg2.extras import RealDictCursor
import os 
from dotenv import load_dotenv
load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")

def get_db_connection():
    """Create a connection to the PostgreSQL database."""
    return psycopg2.connect(DATABASE_URL)

def initialize_db():
    """Initialize the database with the books table if it doesn't exist."""
    conn = get_db_connection()
    cur = conn.cursor()
    try:
        cur.execute("""
            CREATE TABLE IF NOT EXISTS books (
                id SERIAL PRIMARY KEY,
                title TEXT NOT NULL,
                author TEXT NOT NULL,
                year INTEGER NOT NULL,
                genre TEXT NOT NULL,
                read BOOLEAN NOT NULL
            )
        """)
        conn.commit()
    except Exception as e:
        st.error(f"Database initialization error: {e}")
    finally:
        cur.close()
        conn.close()

def load_library():
    """Load the library from the database."""
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    try:
        cur.execute("SELECT * FROM books ORDER BY title")
        return cur.fetchall()
    except Exception as e:
        st.error(f"Error loading library: {e}")
        return []
    finally:
        cur.close()
        conn.close()

def add_book_to_db(book):
    """Add a book to the database."""
    conn = get_db_connection()
    cur = conn.cursor()
    try:
        cur.execute(
            "INSERT INTO books (title, author, year, genre, read) VALUES (%s, %s, %s, %s, %s)",
            (book["title"], book["author"], book["year"], book["genre"], book["read"])
        )
        conn.commit()
        return True
    except Exception as e:
        st.error(f"Error adding book: {e}")
        conn.rollback()
        return False
    finally:
        cur.close()
        conn.close()

def remove_book_from_db(book_id):
    """Remove a book from the database by ID."""
    conn = get_db_connection()
    cur = conn.cursor()
    try:
        cur.execute("DELETE FROM books WHERE id = %s", (book_id,))
        conn.commit()
        return True
    except Exception as e:
        st.error(f"Error removing book: {e}")
        conn.rollback()
        return False
    finally:
        cur.close()
        conn.close()

# Initialize database
initialize_db()

# Streamlit Page Configurations
st.set_page_config(page_title="📚 Personal Library Manager", page_icon="📖", layout="wide")

# Custom Styles - Enhanced UI
st.markdown(
    """
    <style>
    .stApp {
        background: linear-gradient(to right, #1E3A8A, #40E0D0);
        color: black;
        font-family: Arial, sans-serif;
    }
    
    .css-1d391kg { /* Sidebar background */
        background: linear-gradient(to bottom, #0284C7, #06B6D4);
        color: black;
    }
    
    .css-18e3th9 { /* Main content background */
        background: linear-gradient(to right, #1E40AF, #3B82F6);
        color: white;
    }
    
    h1, h2, h3, h4, h5, h6 {
        font-size: 48px !important;
        font-weight: bold;
        text-align: center;
    }
    
    .big-font {
        font-size: 32px !important;
        font-weight: bold;
        color: #FACC15;
    }
    
    .stButton>button {
        border-radius: 12px;
        font-size: 20px;
        padding: 12px 24px;
        background: linear-gradient(to right, #F97316, #EA580C);
        color: white;
        border: none;
        font-weight: bold;
    }
    
    .stButton>button:hover {
        background: black;
        transition: 0.3s;
    }
    
    .stTextInput>label, .stNumberInput>label, .stRadio>label {
        font-size: 20px;
        font-weight: bold;
        color: #FACC15;
    }
    
    .delete-btn {
        background-color: #DC2626 !important;
        color: white;
        border-radius: 8px;
        padding: 5px 10px;
        font-size: 14px;
        margin-left: 10px;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# Sidebar Menu
st.sidebar.title("📖 Library Manager")
menu = st.sidebar.radio("Navigation", ["📘 Add a Book", "🔍 Search Books", "📚 View All Books", "📊 Statistics", "❌ Remove Books"])

# Function to add a book
def add_book():
    st.header("📘 Add a New Book")
    title = st.text_input("📖 Title")
    author = st.text_input("✍️ Author")
    year = st.number_input("📅 Publication Year", min_value=1000, max_value=9999, step=1)
    genre = st.text_input("📂 Genre")
    read_status = st.radio("✅ Have you read this book?", ("Yes", "No"))
    
    if st.button("➕ Add Book"):
        if not title or not author:
            st.warning("Title and author are required!")
            return
            
        new_book = {
            "title": title,
            "author": author,
            "year": int(year),
            "genre": genre,
            "read": True if read_status == "Yes" else False,
        }
        
        if add_book_to_db(new_book):
            st.success(f"📖 '{title}' by {author} added successfully! 🎉")

# Function to search books
def search_books():
    st.header("🔍 Search for a Book")
    search_query = st.text_input("Enter title or author")
    if st.button("🔎 Search"):
        if not search_query:
            st.warning("Please enter a search term")
            return
            
        conn = get_db_connection()
        cur = conn.cursor(cursor_factory=RealDictCursor)
        try:
            cur.execute(
                "SELECT * FROM books WHERE title ILIKE %s OR author ILIKE %s ORDER BY title",
                (f"%{search_query}%", f"%{search_query}%")
            )
            results = cur.fetchall()
            
            if results:
                for book in results:
                    st.markdown(f"📖 **{book['title']}** by {book['author']} ({book['year']}) - *{book['genre']}* - {'✅ Read' if book['read'] else '📌 Unread'}")
            else:
                st.warning("No books found! 😕")
        except Exception as e:
            st.error(f"Search error: {e}")
        finally:
            cur.close()
            conn.close()

# Function to display all books
def view_books():
    st.header("📚 Your Library Collection")
    library = load_library()
    
    if library:
        for book in library:
            st.markdown(f"📖 **{book['title']}** by {book['author']} ({book['year']}) - *{book['genre']}* - {'✅ Read' if book['read'] else '📌 Unread'}")
    else:
        st.info("No books in your library yet. Add some! 📚")

# Function to display statistics
def view_statistics():
    st.header("📊 Library Statistics")
    conn = get_db_connection()
    cur = conn.cursor()
    
    try:
        # Total books
        cur.execute("SELECT COUNT(*) FROM books")
        total_books = cur.fetchone()[0]
        
        # Read books
        cur.execute("SELECT COUNT(*) FROM books WHERE read = TRUE")
        read_books = cur.fetchone()[0]
        
        # Genre statistics
        cur.execute("SELECT genre, COUNT(*) FROM books GROUP BY genre ORDER BY COUNT(*) DESC")
        genre_stats = cur.fetchall()
        
        # Calculate percentage read
        percentage_read = (read_books / total_books * 100) if total_books > 0 else 0
        
        # Display metrics
        st.metric(label="📚 Total Books", value=total_books)
        st.metric(label="📖 Books Read", value=f"{read_books} ({percentage_read:.2f}%)")
        
        # Display genre breakdown
        if genre_stats:
            st.subheader("Genre Breakdown")
            for genre, count in genre_stats:
                st.text(f"{genre}: {count} books")
    except Exception as e:
        st.error(f"Error loading statistics: {e}")
    finally:
        cur.close()
        conn.close()

# Function to remove books
def remove_books():
    st.header("❌ Remove Books")
    library = load_library()
    
    if not library:
        st.info("No books in your library yet. Add some! 📚")
        return
    
    for book in library:
        col1, col2 = st.columns([5, 1])
        with col1:
            st.markdown(f"📖 **{book['title']}** by {book['author']} ({book['year']}) - *{book['genre']}* - {'✅ Read' if book['read'] else '📌 Unread'}")
        with col2:
            if st.button("Delete", key=f"delete_{book['id']}", help=f"Delete {book['title']}", type="primary"):
                if remove_book_from_db(book['id']):
                    st.success(f"'{book['title']}' has been removed from your library.")
                    st.rerun()

# Render selected menu option
if menu == "📘 Add a Book":
    add_book()
elif menu == "🔍 Search Books":
    search_books()
elif menu == "📚 View All Books":
    view_books()
elif menu == "📊 Statistics":
    view_statistics()
elif menu == "❌ Remove Books":
    remove_books()
