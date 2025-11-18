import os
import csv
from flask import Flask, jsonify, render_template
from flask_sqlalchemy import SQLAlchemy

#this function is added with help of AI since there was debugging issues initially
def to_float_or_none(value):
    if value is None or (isinstance(value, str) and value.strip() == ''):
        return None
    try:
        return float(str(value).replace(',', '').strip())
    except (ValueError, TypeError):
        return None

basedir = os.path.abspath(os.path.dirname(__file__))
app = Flask(__name__)

if os.environ.get('DATABASE_URL'):
    uri = os.environ.get('DATABASE_URL')
    if isinstance(uri, str) and uri.startswith('postgres://'):
        uri = uri.replace('postgres://', 'postgresql://', 1)
    app.config['SQLALCHEMY_DATABASE_URI'] = uri
else:
    basedir = os.path.abspath(os.path.dirname(__file__))
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'ipos.db')

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


class IPO(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.String(20), nullable=False) 
    ipo_name = db.Column(db.String(255), nullable=False)
    issue_size_crores = db.Column(db.Float, nullable=True) 
    qib = db.Column(db.Float, nullable=True) 
    hni = db.Column(db.Float, nullable=True) 
    rii = db.Column(db.Float, nullable=True) 
    total_subscription = db.Column(db.Float, nullable=True) 
    offer_price = db.Column(db.Float, nullable=True)
    list_price = db.Column(db.Float, nullable=True)
    listing_gain = db.Column(db.Float, nullable=True)
    cmp_bse = db.Column(db.Float, nullable=True) 
    cmp_nse = db.Column(db.Float, nullable=True) 
    current_gains = db.Column(db.Float, nullable=True) 

    def __repr__(self):
        return (
            f"IPO Name: {self.ipo_name}, Date: {self.date}, "
            f"Issue Size (Cr): {self.issue_size_crores}, "
            f"Subscription (x): {self.total_subscription}, "
            f"Offer Price: {self.offer_price}, "
            f"List Price: {self.list_price}, "
            f"Listing Gain (%): {self.listing_gain}, "
            f"Current Gains (%): {self.current_gains}"
        )

with app.app_context():
    db.create_all()

#os commands and usages are learnt by me from AI 
@app.route('/load-data')
def load_csv_data():
    file_path = os.path.join(basedir, 'ipo_data.csv')
    IPO.query.delete()
    db.session.commit()

    records_added = 0
    with open(file_path, mode='r', encoding='windows-1252') as csvfile:
        reader = csv.DictReader(csvfile)
        column_map = {
            'Date': 'date', 'IPO_Name': 'ipo_name', 'Issue_Size(crores)': 'issue_size_crores', 
            'QIB': 'qib', 'HNI': 'hni', 'RII': 'rii', 'Total': 'total_subscription', 
            'Offer Price': 'offer_price', 'List Price': 'list_price', 
            'Listing Gain': 'listing_gain', 'CMP(BSE)': 'cmp_bse', 
            'CMP(NSE)': 'cmp_nse', 'Current Gains': 'current_gains'
        }

        for row in reader:
            if row.get('Date', '').strip() == 'Date' or row.get('IPO_Name', '').strip() == 'Date':
                continue

            if not row.get('Date') or not row.get('IPO_Name'):
                continue

            data = {}
            for csv_header, model_attr in column_map.items():
                value = row.get(csv_header)
                if model_attr not in ['date', 'ipo_name']:
                    data[model_attr] = to_float_or_none(value)
                else:
                    data[model_attr] = value
            ipo = IPO(**data)
            db.session.add(ipo)
            records_added = records_added + 1

    db.session.commit()
    return jsonify({
        "message": f"Successfully loaded and added {records_added} IPO records from 'ipo_data.csv'.",
        "info": "Please refresh the page."
    })

@app.route('/')
def home():
    return render_template('website.html')

@app.route('/companies')
def companies():
    ipo_records = IPO.query.all() 
    return render_template('Companies.html', ipo_records=ipo_records)

@app.route('/calendar')
def calendar():
    return render_template('Calendar.html')

@app.route('/dive_deeper_with_ai')
def dive_deeper_with_ai():
    return render_template('Dive_Deeper_with_AI.html')

@app.route('/learning_videos')
def learning_videos():
    return render_template('Learning_Videos.html')

if __name__ == '__main__':
    app.run(debug=True)