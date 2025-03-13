import json
import streamlit as st

LIBRARY_FILE = "library.json"

def load_library():
    """Load the library from a JSON file."""
    try:
        with open(LIBRARY_FILE, "r") as file:
            return json.load(file)
    except (FileNotFoundError, json.JSONDecodeError):
        return []

def save_library(library):
    """Save the library to a JSON file."""
    with open(LIBRARY_FILE, "w") as file:
        json.dump(library, file, indent=4)

# Load library data
library = load_library()

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
    </style>
    """,
    unsafe_allow_html=True,
)

# Sidebar Menu
st.sidebar.title("📖 Library Manager")
menu = st.sidebar.radio("Navigation", ["📘 Add a Book", "🔍 Search Books", "📚 View All Books", "📊 Statistics"])

# Function to add a book
def add_book():
    st.header("📘 Add a New Book")
    title = st.text_input("📖 Title")
    author = st.text_input("✍️ Author")
    year = st.number_input("📅 Publication Year", min_value=1000, max_value=9999, step=1)
    genre = st.text_input("📂 Genre")
    read_status = st.radio("✅ Have you read this book?", ("Yes", "No"))
    
    if st.button("➕ Add Book"):
        new_book = {
            "title": title,
            "author": author,
            "year": int(year),
            "genre": genre,
            "read": True if read_status == "Yes" else False,
        }
        library.append(new_book)
        save_library(library)
        st.success(f"📖 '{title}' by {author} added successfully! 🎉")

# Function to search books
def search_books():
    st.header("🔍 Search for a Book")
    search_query = st.text_input("Enter title or author")
    if st.button("🔎 Search"):
        results = [book for book in library if search_query.lower() in book["title"].lower() or search_query.lower() in book["author"].lower()]
        if results:
            for book in results:
                st.markdown(f"📖 **{book['title']}** by {book['author']} ({book['year']}) - *{book['genre']}* - {'✅ Read' if book['read'] else '📌 Unread'}")
        else:
            st.warning("No books found! 😕")

# Function to display all books
def view_books():
    st.header("📚 Your Library Collection")
    if library:
        for book in library:
            st.markdown(f"📖 **{book['title']}** by {book['author']} ({book['year']}) - *{book['genre']}* - {'✅ Read' if book['read'] else '📌 Unread'}")
    else:
        st.info("No books in your library yet. Add some! 📚")

# Function to display statistics
def view_statistics():
    st.header("📊 Library Statistics")
    total_books = len(library)
    read_books = sum(1 for book in library if book["read"])
    percentage_read = (read_books / total_books * 100) if total_books > 0 else 0
    st.metric(label="📚 Total Books", value=total_books)
    st.metric(label="📖 Books Read", value=f"{read_books} ({percentage_read:.2f}%)")

# Render selected menu option
if menu == "📘 Add a Book":
    add_book()
elif menu == "🔍 Search Books":
    search_books()
elif menu == "📚 View All Books":
    view_books()
elif menu == "📊 Statistics":
    view_statistics()
