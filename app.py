from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///comments.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

class Comment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    author = db.Column(db.String(100), nullable=False)
    text = db.Column(db.Text, nullable=False)
    date_posted = db.Column(db.DateTime, default=datetime.utcnow)


@app.route("/")
def index():
    return render_template("index.html")

@app.route('/about', methods=['GET', 'POST'])
def about():
    error = None
    author_filter = request.args.get('author')
    
    if request.method == 'POST':
        author_name = request.form.get('author', '').strip()
        comment_text = request.form.get('text', '').strip()
        
        if not author_name or not comment_text:
            error = "Пожалуйста, заполните все поля!"
        else:
            new_comment = Comment(author=author_name, text=comment_text)
            db.session.add(new_comment)
            db.session.commit()
            return redirect(url_for('about'))
            
    if author_filter:
        comments = Comment.query.filter_by(author=author_filter).order_by(Comment.date_posted.desc()).all()
    else:
        comments = Comment.query.order_by(Comment.date_posted.desc()).all()
        
    return render_template('about.html', comments=comments, error=error, author_filter=author_filter)


@app.route("/changelog")
def changelog():
    return render_template("changelog.html")

@app.route("/hobbys")
def hobbys():
    return render_template("hobbys.html")

@app.route('/tests', methods=['GET', 'POST'])
def tests():
    score = None
    total_questions = 6
    
    if request.method == 'POST':
        score = 0
        if request.form.get('q1') == 'yes':
            score += 1
        if request.form.get('q2') == 'yes':
            score += 1
        if request.form.get('q3') == 'yes':
            score += 1
        if request.form.get('q4') == 'yes':
            score += 1
        if request.form.get('q5') == 'no':
            score += 1
        if request.form.get('q6') == 'yes':
            score += 1
    return render_template('tests.html', score=score, total=total_questions)

def calculate_life_path(date_str):
    if not date_str:
        return 0
    digits = [int(d) for d in date_str if d.isdigit()]
    total = sum(digits)
    while total > 9:
        total = sum(int(d) for d in str(total))
    return total

def get_love_text(union_number):
    texts = {
        1: "Отношения-соперничество. Много страсти и борьбы за власть. Важно стать союзниками!",
        2: "Гармония и доверие. Вы отлично дополняете друг друга, создавая уют и тепло.",
        3: "Яркий и творческий союз. Вместе весело, но нужно учиться контролировать эмоции.",
        4: "Крепкий и стабильный союз. Вы цените труд и надежность друг в друге.",
        5: "Союз свободы и приключений. Много путешествий и романтики.",
        6: "Семейный союз. Для вас обоих важны дом, уют и забота друг о друге.",
        7: "Духовная и интеллектуальная связь. Вы — лучшие друзья и партнеры.",
        8: "Союз амбиций и успеха. Вместе вы можете достичь больших высот.",
        9: "Идеалистичный и мудрый союз. Вы смотрите в одном направлении.",
    }
    return texts.get(union_number, "Это редкое сочетание, полное загадок и открытий!")

@app.route('/numerology', methods=['GET', 'POST'])
def numerology():
    result = None
    if request.method == 'POST':
        date1 = request.form.get('date1')
        date2 = request.form.get('date2')
        
        if date1 and date2:
            lp1 = calculate_life_path(date1)
            lp2 = calculate_life_path(date2)
            
            union = lp1 + lp2
            while union > 9:
                union = sum(int(d) for d in str(union))
                
            result = {
                'lp1': lp1,
                'lp2': lp2,
                'union': union,
                'text': get_love_text(union)
            }
            
    return render_template('numerology.html', result=result)

@app.route('/cats')
def cats():
    return render_template('cats.html')

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)