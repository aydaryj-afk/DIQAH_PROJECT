import sqlite3
import os
import requests
from flask import Flask, request, jsonify, render_template, session, redirect, url_for

app = Flask(__name__)
app.secret_key = "diqah_secure_secret_key"

from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing.sequence import pad_sequences
import pickle
model = load_model("lstm_model.h5")

with open("tokenizer.pkl", "rb") as f:
    tokenizer = pickle.load(f)
    

# ================= CONFIG =================
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "diqah.db")

# ================= DB =================
def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row  # Allow accessing columns by name
    return conn


# ================= SPLASH =================
@app.route('/')
def splash():
    if 'username' in session:
        return redirect(url_for('main_page'))
    return render_template("index.html")


# ================= LOGIN PAGE =================
@app.route('/login')
def home():
    if 'username' in session:
        return redirect(url_for('main_page'))
    return render_template("login.html")


# ================= LOGIN =================
@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()

    email = data.get("email")
    password = data.get("password")

    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT * FROM users
        WHERE LOWER(email)=LOWER(?) AND password=?
    """, (email, password))

    user = cursor.fetchone()
    conn.close()

    if user:
        session['user_id'] = user['id']
        session['username'] = user['username']
        return jsonify({
    "status": "success",
    "username": user["username"]
})
    else:
        return jsonify({"status": "not_found"})

#================== GEUST==================
@app.route('/guest')
def guest():
    session.clear()
    session['guest'] = True
    return redirect('/main')

# ================= LOGOUT =================
@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('home'))


# ================= SIGNUP PAGE =================
@app.route('/signup_page')
def signup_page():
    return render_template("signup.html")


# ================= SIGNUP =================
@app.route('/signup', methods=['POST'])
def signup():
    data = request.get_json()

    username = data.get("username")
    email = data.get("email")
    age = data.get("age")
    password = data.get("password")

    conn = get_db()
    cursor = conn.cursor()

    # 🔹 تحقق من username
    cursor.execute("SELECT * FROM users WHERE username=?", (username,))
    if cursor.fetchone():
        conn.close()
        return jsonify({"status": "username_exists"})

    # 🔹 تحقق من email
    cursor.execute("SELECT * FROM users WHERE email=?", (email,))
    if cursor.fetchone():
        conn.close()
        return jsonify({"status": "email_exists"})

    try:
        cursor.execute("""
            INSERT INTO users (username, name, email, age, password, phone)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (username, username, email, age, password, ""))

        conn.commit()
        conn.close()

        return jsonify({"status": "success"})

    except Exception as e:
        print("ERROR:", e)
        conn.close()
        return jsonify({"status": "error"})


# ================= FORGOT PASSWORD =================
@app.route('/forgot_password')
def forgot_password_page():
    return render_template("forgot_password.html")


# ================= MAIN HOME =================
@app.route('/main')
def main_page():
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM news LIMIT 5")
    news = cursor.fetchall()

    conn.close()
    return render_template("home.html", news=news)



# ================= HISTORY =================
@app.route('/history')
def history():
    return render_template("history.html")


# ================= PROFILE =================
@app.route('/profile')
def profile():
    if 'user_id' not in session:
        return render_template("profile.html", user=None)
    
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE id=?", (session['user_id'],))
    user = cursor.fetchone()
    conn.close()
    
    return render_template("profile.html", user=user)


# ================= SEARCH =================
@app.route('/search')
def search():
    
    return render_template("search.html")


# ================= CHECK PAGE =================
@app.route('/check')
def check_page():
    return render_template("check.html")


@app.route('/bookmarks')
def bookmarks():
     if 'guest' in session:
      return redirect('/login')
     return render_template("bookmarks.html")


@app.route('/language')
def language():
    return render_template("language.html")


@app.route('/tips')
def tips():
    return render_template("tips.html")


@app.route('/about_us')
def about_us():
    return render_template("about_us.html")


@app.route('/contact_us')
def contact_us():
    return render_template("contact_us.html")

@app.route('/edit_profile')
def edit_profile():
    if 'user_id' not in session:
        return render_template("profile.html", user=None)
    
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE id=?", (session['user_id'],))
    user = cursor.fetchone()
    conn.close()
    
    return render_template("edit_profile.html", user=user)


@app.route('/update_profile', methods=['POST'])
def update_profile():
    if 'user_id' not in session:
        return jsonify({"status": "error", "message": "Not logged in"})
    
    data = request.get_json()
    name = data.get("name")
    email = data.get("email")
    age = data.get("age")
    password = data.get("password")
    
    conn = get_db()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            UPDATE users 
            SET name=?, email=?, age=?, password=? 
            WHERE id=?
        """, (name, email, age, password, session['user_id']))
        conn.commit()
        conn.close()
        return jsonify({"status": "success"})
    except Exception as e:
        print("UPDATE ERROR:", e)
        conn.close()
        return jsonify({"status": "error", "message": str(e)})


@app.route('/get_channels')
def get_channels():
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("SELECT id, name, logo FROM channels")
    rows = cursor.fetchall()

    conn.close()

    return jsonify([
        {"id": row[0], "name": row[1], "logo": row[2]}
        for row in rows
    ])

@app.route('/get_news')
def get_news():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT id, title, image FROM news ORDER BY id DESC")
    rows = cursor.fetchall()
    conn.close()
    return jsonify([list(row) for row in rows])


@app.route('/recent_news')
def recent_news():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT id, title, image FROM news ORDER BY id DESC")
    news_list = cursor.fetchall()
    conn.close()
    return render_template("recent_news.html", news=news_list)


@app.route('/news/<int:news_id>')
def news_detail(news_id):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM news WHERE id = ?", (news_id,))
    news_item = cursor.fetchone()
    conn.close()
    if news_item:
        return render_template("news_detail.html", news=news_item)
    return "News not found", 404


# ================= AI ANALYZE  =================
@app.route('/analyze', methods=['POST'])
def analyze():
    data = request.get_json()
    news_text = data.get("text")

    if not news_text:
        return jsonify({"error": "No text provided"}), 400

    sequence = tokenizer.texts_to_sequences([news_text])
    padded = pad_sequences(sequence, maxlen=200)

    prediction = model.predict(padded)[0][0]

    #  تصحيح النتيجة
    if prediction > 0.5:
        verdict = "Fake"
        score = round(prediction * 100, 2)
    else:
        verdict = "Real"
        score = round((1 - prediction) * 100, 2)

    explanation = "Predicted using LSTM model"

    
    user_id = session.get('user_id', 1)

    conn = get_db()
    cursor = conn.cursor()

    cursor.execute(
        "INSERT INTO check_history (user_id, news_text, result, explanation) VALUES (?, ?, ?, ?)",
        (user_id, news_text, verdict, explanation)
    )

    conn.commit()
    conn.close()

    return jsonify({
        "verdict": verdict,
        "score": score,
        "explanation": explanation
    })

@app.route('/get_history')
def get_history():

    if 'user_id' not in session:
        return jsonify([])

    user_id = session['user_id']  

    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT news_text, result, explanation, created_at 
        FROM check_history 
        WHERE user_id = ? 
        ORDER BY created_at DESC
    """, (user_id,))

    rows = cursor.fetchall()
    conn.close()

    history = []
    for row in rows:
        history.append({
            "text": row["news_text"],
            "result": row["result"],
            "explanation": row["explanation"],
            "date": row["created_at"]
        })

    return jsonify(history)   

#=================== Clear history =============
@app.route('/clear_history', methods=['POST'])
def clear_history():
    print(" CLEAR HISTORY CALLED")

    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM check_history")
    conn.commit()
    conn.close()

    return jsonify({"status": "success"})



# ================= AUTHOR PROFILE =================

@app.route('/author/<int:id>')
def author_profile(id):
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM channels WHERE id=?", (id,))
    author = cursor.fetchone()

    cursor.execute("SELECT * FROM news WHERE author_id=? ORDER BY id DESC", (id,))
    news = cursor.fetchall()

    conn.close()

    return render_template("AuthorProfile.html",
                           author=author,
                           news=news,
                           username=session.get('username'))

#=============== follow of profile athour=============
@app.route('/follow', methods=['POST'])
def follow():
    if 'user_id' not in session:
        return jsonify({"status": "not_logged_in"})

    data = request.get_json()
    channel_id = data.get("channel_id")
    user_id = session['user_id']

    conn = get_db()
    cursor = conn.cursor()

    # هل متابع قبل؟
    cursor.execute("SELECT * FROM follows WHERE user_id=? AND channel_id=?", (user_id, channel_id))
    if cursor.fetchone():
        conn.close()
        return jsonify({"status": "already_following"})

    cursor.execute("INSERT INTO follows (user_id, channel_id) VALUES (?, ?)", (user_id, channel_id))
    conn.commit()
    conn.close()

    return jsonify({"status": "success"})

@app.route('/check_follow/<int:channel_id>')
def check_follow(channel_id):
    if 'user_id' not in session:
        return jsonify({"following": False})

    user_id = session['user_id']

    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT * FROM follows 
        WHERE user_id=? AND channel_id=?
    """, (user_id, channel_id))

    follow = cursor.fetchone()
    conn.close()

    return jsonify({"following": True if follow else False})

#======================= unfollow author ======================
@app.route('/unfollow', methods=['POST'])
def unfollow():
    if 'user_id' not in session:
        return jsonify({"status": "not_logged_in"})

    data = request.get_json()
    channel_id = int(data.get("channel_id"))
    user_id = session['user_id']

    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("""
        DELETE FROM follows 
        WHERE user_id=? AND channel_id=?
    """, (user_id, channel_id))

    conn.commit()
    conn.close()

    return jsonify({"status": "success"})

#================= news follwing=====================
@app.route('/following_news')
def following_news():

    if 'user_id' not in session:
        return jsonify([])

    user_id = session['user_id']

    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT news.* FROM news
        JOIN follows ON news.author_id = follows.channel_id
        WHERE follows.user_id = ?
        ORDER BY news.id DESC
    """, (user_id,))

    news = cursor.fetchall()
    conn.close()

    result = []
    for n in news:
        result.append({
            "id": n["id"],
            "title": n["title"],
            "image": n["image"],
            "time": n["time"]
        })

    return jsonify(result)

# ================= SAVE BOOKMARK =================
@app.route('/save_bookmark', methods=['POST'])
def save_bookmark():

    data = request.get_json()
    user_id = session.get('user_id')
    news_id = data.get('news_id')

    conn = get_db()
    cursor = conn.cursor()

    # تحقق هل محفوظ مسبقاً
    cursor.execute("""
        SELECT id FROM bookmarks
        WHERE user_id = ? AND news_id = ?
    """, (user_id, news_id))

    existing = cursor.fetchone()

    # toggle (حذف / إضافة)
    if existing:
        cursor.execute(
            "DELETE FROM bookmarks WHERE user_id=? AND news_id=?",
            (user_id, news_id)
        )
        conn.commit()
        conn.close()
        return jsonify({"status": "removed"})
    else:
        cursor.execute("""
            INSERT INTO bookmarks (user_id, news_id)
            VALUES (?, ?)
        """, (user_id, news_id))

        conn.commit()
        conn.close()
        return jsonify({"status": "saved"})


# ================= GET BOOKMARKS =================
@app.route('/get_bookmarks')
def get_bookmarks():

    user_id = session.get('user_id')

    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("""
    SELECT news.id, news.title, news.source, news.body, news.image
    FROM bookmarks
    JOIN news ON bookmarks.news_id = news.id
    WHERE bookmarks.user_id = ?
    ORDER BY bookmarks.id DESC
    """, (user_id,))

    rows = cursor.fetchall()
    conn.close()

    return jsonify([dict(row) for row in rows])
#============================================================
@app.route('/check_bookmark')
def check_bookmark():

    user_id = session.get('user_id')
    news_id = request.args.get('news_id')

    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT id FROM bookmarks
        WHERE user_id = ? AND news_id = ?
    """, (user_id, news_id))

    existing = cursor.fetchone()
    conn.close()

    return jsonify({"saved": True if existing else False})
    # ================= CLEAR BOOKMARKS =================
@app.route('/clear_bookmarks', methods=['POST'])
def clear_bookmarks():
    user_id = session.get('user_id')

    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("DELETE FROM bookmarks WHERE user_id = ?", (user_id,))
    
    conn.commit()
    conn.close()

    return jsonify({"status": "success"})

# ================= ADMIN LOGIN PAGE =================
@app.route('/admin')
def admin_page():
    return render_template("log_in.html")


# ================= ADMIN LOGIN =================
@app.route('/admin_login', methods=['POST'])
def admin_login():
    data = request.get_json()

    username = data.get("username")
    password = data.get("password")

    conn = get_db()
    cursor = conn.cursor()

    cursor.execute(
        "SELECT * FROM admins WHERE username=? AND password=?",
        (username, password)
    )

    admin = cursor.fetchone()
    conn.close()

    if admin:
        session['admin'] = username
        return jsonify({"status": "success"})
    else:
        return jsonify({"status": "not_found"})


# ================= ADMIN DASHBOARD =================
@app.route('/admin_dashboard')
def admin_dashboard():

    if 'admin' not in session:
        return redirect('/admin')

    conn = get_db()
    cursor = conn.cursor()

    # عدد المستخدمين
    cursor.execute("SELECT COUNT(*) FROM users")
    users_count = cursor.fetchone()[0]

    # عدد الأخبار
    cursor.execute("SELECT COUNT(*) FROM news")
    news_count = cursor.fetchone()[0]

    # القنوات
    cursor.execute("SELECT name FROM channels LIMIT 5")
    channels = cursor.fetchall()

    # آخر الأخبار
    cursor.execute("SELECT title, source FROM news ORDER BY id DESC LIMIT 4")
    latest_news = cursor.fetchall()

    conn.close()

    return render_template(
        "main.html",
        channels=channels,
        latest_news=latest_news,
        users_count=users_count,
        news_count=news_count,
        admin_name=session['admin']
    )


#==================== manage feedback================

@app.route('/manage_feedback')
def manage_feedback():

    if 'admin' not in session:
        return redirect('/admin')

    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("""
    SELECT feedback.id,
           users.username,
           feedback.message,
           feedback.category,
           feedback.status,
           feedback.priority
    FROM feedback
    JOIN users ON feedback.user_id = users.id
    ORDER BY feedback.id DESC
    """)

    feedbacks = cursor.fetchall()

    cursor.execute("SELECT COUNT(*) FROM feedback")
    total = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM feedback WHERE status='Resolved'")
    resolved = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM feedback WHERE status='Pending'")
    new_count = cursor.fetchone()[0]

    conn.close()

    return render_template(
        "manage_feedback.html",
        feedbacks=feedbacks,
        total=total,
        resolved=resolved,
        new_count=new_count,
        admin_name=session['admin']
    )


#==================== feedback details================

@app.route('/feedback/<int:id>')
def feedback_details(id):

    if 'admin' not in session:
        return redirect('/admin')

    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("""
    SELECT feedback.id,
           users.username,
           users.email,
           feedback.message,
           feedback.category,
           feedback.status,
           feedback.priority,
           feedback.created_at
    FROM feedback
    JOIN users ON feedback.user_id = users.id
    WHERE feedback.id = ?
    """, (id,))

    item = cursor.fetchone()
    conn.close()

    return render_template(
        "feedback_details.html",
        item=item,
        admin_name=session['admin']
    )


#==================== manage users================

@app.route('/manage_users')
def manage_users():

    if 'admin' not in session:
        return redirect('/admin')

    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("""
    SELECT id, name, email, username
    FROM users
    ORDER BY id DESC
    """)

    users = cursor.fetchall()

    cursor.execute("SELECT COUNT(*) FROM users")
    total_users = cursor.fetchone()[0]

    conn.close()

    return render_template(
        "manage_user.html",
        users=users,
        total_users=total_users,
        admin_name=session['admin']
    )


# ================= UPDATE FEEDBACK =================
@app.route('/update_feedback/<int:id>', methods=['POST'])
def update_feedback(id):

    if 'admin' not in session:
        return redirect('/admin')

    status = request.form['status']
    priority = request.form['priority']

    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("""
    UPDATE feedback
    SET status=?, priority=?
    WHERE id=?
    """, (status, priority, id))

    conn.commit()
    conn.close()

    return redirect(f'/feedback/{id}')


# ================= DELETE USER =================
@app.route('/delete_user/<int:id>')
def delete_user(id):

    if 'admin' not in session:
        return redirect('/admin')

    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("DELETE FROM users WHERE id=?", (id,))
    conn.commit()
    conn.close()

    return redirect('/manage_users')


# ================= ADD NEWS =================
@app.route('/add_news', methods=['POST'])
def add_news():

    if 'admin' not in session:
        return redirect('/admin')

    title = request.form['title']
    source_id = request.form['source_id']

    conn = get_db()
    cursor = conn.cursor()

    # إذا الخبر خارجي
    if source_id == "external":
        source_name = "External"
    else:
        # نجيب اسم القناة من جدول channels
        cursor.execute("SELECT name FROM channels WHERE id=?", (source_id,))
        channel = cursor.fetchone()
        source_name = channel[0] if channel else "Unknown"

    cursor.execute("""
    INSERT INTO news(title, body, image, source, time, author_id)
    VALUES(?,?,?,?,?,?)
    """, (
        title,
        "Added by admin",
        "",
        source_name,
        "Now",
        1
    ))

    conn.commit()
    conn.close()

    return redirect('/manage_news')



# ================= EDIT USER =================
@app.route('/edit_user/<int:id>')
def edit_user(id):

    if 'admin' not in session:
        return redirect('/admin')

    name = request.args.get('name')
    email = request.args.get('email')
    username = request.args.get('username')

    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("""
    UPDATE users
    SET name=?, email=?, username=?
    WHERE id=?
    """, (name, email, username, id))

    conn.commit()
    conn.close()

    return redirect('/manage_users')


@app.route('/manage_channels')
def manage_channels():

    if 'admin' not in session:
        return redirect('/admin')

    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM channels")
    channels = cursor.fetchall()

    conn.close()

    return render_template(
        "manage_channels.html",
        channels=channels,
        admin_name=session['admin']
    )


@app.route('/add_channel', methods=['POST'])
def add_channel():

    if 'admin' not in session:
        return redirect('/admin')

    name = request.form['name']

    conn = get_db()
    cursor = conn.cursor()

    cursor.execute(
        "INSERT INTO channels(name, logo) VALUES(?, ?)",
        (name, "default")
    )

    conn.commit()
    conn.close()

    return redirect('/manage_channels')


@app.route('/delete_channel/<int:id>')
def delete_channel(id):

    if 'admin' not in session:
        return redirect('/admin')

    conn = get_db()
    cursor = conn.cursor()

    cursor.execute(
        "DELETE FROM channels WHERE id=?",
        (id,)
    )

    conn.commit()
    conn.close()

    return redirect('/manage_channels')


@app.route('/manage_news')
def manage_news():

    if 'admin' not in session:
        return redirect('/admin')

    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM news ORDER BY id DESC")
    news = cursor.fetchall()

    # الجديد
    cursor.execute("SELECT * FROM channels")
    channels = cursor.fetchall()

    conn.close()

    return render_template(
        "manage_news.html",
        news=news,
        channels=channels,   
        admin_name=session['admin']
    )




@app.route('/delete_news/<int:id>')
def delete_news(id):

    if 'admin' not in session:
        return redirect('/admin')

    conn = get_db()
    cursor = conn.cursor()

    cursor.execute(
        "DELETE FROM news WHERE id=?",
        (id,)
    )

    conn.commit()
    conn.close()

    return redirect('/manage_news')



@app.route('/manage_tips')
def manage_tips():

    if 'admin' not in session:
        return redirect('/admin')

    tips = [
        "Always check the source before sharing news",
        "Look for multiple trustworthy sources",
        "Verify dates and authors",
        "Don't rely on social media only",
        "Read full article before sharing"
    ]

    return render_template(
        "manage_tips.html",
        tips=tips
    )

@app.route('/save_tips', methods=['POST'])
def save_tips():

    if 'admin' not in session:
        return redirect('/admin')

    tip1 = request.form['tip1']
    tip2 = request.form['tip2']
    tip3 = request.form['tip3']
    tip4 = request.form['tip4']
    tip5 = request.form['tip5']

    return redirect('/manage_tips')


# ================= RUN =================
if __name__ == "__main__":
    app.run(debug=True)

