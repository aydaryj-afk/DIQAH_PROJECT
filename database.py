import sqlite3
import os

# ================= مسار ثابت =================
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
db_path = os.path.join(BASE_DIR, "diqah.db")

conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# ================= USERS =================
cursor.execute("""
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    name TEXT NOT NULL,
    email TEXT UNIQUE NOT NULL,
    age INTEGER,
    phone TEXT,
    password TEXT NOT NULL
)
""")

# ================= ADMINS =================
cursor.execute("""
CREATE TABLE IF NOT EXISTS admins (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    password TEXT NOT NULL
)
""")

# إضافة أدمن مرة وحدة فقط
cursor.execute("SELECT COUNT(*) FROM admins")
count_admins = cursor.fetchone()[0]

if count_admins == 0:
   if count_admins == 0:
    cursor.execute("INSERT INTO admins (username,password) VALUES ('areej','Areejadmin1')")
    cursor.execute("INSERT INTO admins (username,password) VALUES ('fajr','Fajradmin2')")
    cursor.execute("INSERT INTO admins (username,password) VALUES ('ryof','Ryofadmin3')")
    cursor.execute("INSERT INTO admins (username,password) VALUES ('layan','Layanadmin4')")

# ================= FEEDBACK =================
cursor.execute("""
CREATE TABLE IF NOT EXISTS feedback (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    message TEXT,
    category TEXT,
    status TEXT,
    priority TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id)
)
""")

# ================= CHANNELS =================
cursor.execute("""
CREATE TABLE IF NOT EXISTS channels (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT,
    logo TEXT
)
""")

#  إضافة القنوات (مرة وحدة فقط)
cursor.execute("SELECT COUNT(*) FROM channels")
count_channels = cursor.fetchone()[0]

if count_channels == 0:
    cursor.execute("INSERT INTO channels (name, logo) VALUES ('BBC NEWS', 'bbc')")
    cursor.execute("INSERT INTO channels (name, logo) VALUES ('CNN NEWS', 'cnn')")
    cursor.execute("INSERT INTO channels (name, logo) VALUES ('ALJAZEERA', 'aljazeera')")
    cursor.execute("INSERT INTO channels (name, logo) VALUES ('SKY NEWS', 'sky')")
    cursor.execute("INSERT INTO channels (name, logo) VALUES ('REUTERS', 'reuters')")
    cursor.execute("INSERT INTO channels (name, logo) VALUES ('FOX NEWS', 'fox')")

# ================= NEWS =================
cursor.execute("""
CREATE TABLE IF NOT EXISTS news (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    body TEXT,
    image TEXT,
    source TEXT,
    time TEXT,
    author_id INTEGER,
    FOREIGN KEY (author_id) REFERENCES channels(id)
)
""")

#  إضافة الأخبار (مرة وحدة فقط)
cursor.execute("SELECT COUNT(*) FROM news")
count_news = cursor.fetchone()[0]

if count_news == 0:
    cursor.execute("""
        INSERT INTO news (title, body, image, source, time, author_id) 
        VALUES ('Breaking: New AI technology released', 'A revolutionary AI model has been launched today...', 'https://images.unsplash.com/photo-1677442136019-21780ecad995', 'BBC NEWS', '2h ago', 1)
    """)
    cursor.execute("""
        INSERT INTO news (title, body, image, source, time, author_id) 
        VALUES ('World: Major global event happening now', 'Thousands gather for the annual international summit...', 'https://images.unsplash.com/photo-1529107386315-e1a2ed48a620', 'CNN NEWS', '4h ago', 2)
    """)
    cursor.execute("""
        INSERT INTO news (title, body, image, source, time, author_id) 
        VALUES ('Economy: Markets rising today', 'Global markets show a steady increase after recent reports...', 'https://images.unsplash.com/photo-1611974714405-0210e74f1b8a', 'REUTERS', '6h ago', 5)
    """)
    cursor.execute("""
        INSERT INTO news (title, body, image, source, time, author_id) 
        VALUES ('Health: New study surprises scientists', 'A new study reveals unexpected benefits of mediterranean diet...', 'https://images.unsplash.com/photo-1505751172876-fa1923c5c528', 'SKY NEWS', '1d ago', 4)
    """)

# ================= HISTORY =================
cursor.execute("""
CREATE TABLE IF NOT EXISTS check_history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    news_text TEXT,
    result TEXT,
    explanation TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id)
)
""")

# ================= BOOKMARKS =================
cursor.execute("""
CREATE TABLE IF NOT EXISTS bookmarks (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    news_id INTEGER,
    FOREIGN KEY (user_id) REFERENCES users(id),
    FOREIGN KEY (news_id) REFERENCES news(id)
);
""")

# ================= FOLLOWS =================
cursor.execute("""
CREATE TABLE IF NOT EXISTS follows (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    channel_id INTEGER,
    FOREIGN KEY (user_id) REFERENCES users(id),
    FOREIGN KEY (channel_id) REFERENCES channels(id)
)
""")


conn.commit()
conn.close()

print(" Database created", db_path)

