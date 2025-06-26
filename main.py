import os
from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, session
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from models import db, User, Vote, VotePreference, init_db
from config import Config

# Initialize Flask app
app = Flask(__name__)
app.config.from_object(Config)

# Initialize extensions
db.init_app(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'admin_login'

# Create database tables
with app.app_context():
    db.create_all()
    init_db()

# Login manager configuration
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Add current year to all templates
@app.context_processor
def inject_now():
    return {'now': datetime.now()}

CANDIDATES = ["Alice Smith", "Bob Johnson", "Charlie Brown", "Diana Miller", "Eve Davis"]

# Routes
@app.route('/')
def home():
    return render_template('index.html')

@app.route('/vote', methods=['GET', 'POST'])
def vote():
    error = None

    if request.method == 'POST':
        preferences = {}
        selected_candidates = set()

        for i in range(1, len(CANDIDATES) + 1):
            candidate = request.form.get(f'pref{i}')
            if candidate:
                if candidate not in CANDIDATES:
                    error = f"Invalid candidate selected: {candidate}"
                    return render_template('vote.html', candidates=CANDIDATES, error=error)
                if candidate in selected_candidates:
                    error = f"You cannot rank the same candidate multiple times: {candidate}"
                    return render_template('vote.html', candidates=CANDIDATES, error=error)
                preferences[str(i)] = candidate
                selected_candidates.add(candidate)

        if not preferences:
            error = "You must select at least your first preference."
            return render_template('vote.html', candidates=CANDIDATES, error=error)

        # Save vote to database
        vote = Vote()
        db.session.add(vote)
        db.session.flush()  # Get the vote ID
        
        for rank, candidate in preferences.items():
            pref = VotePreference(vote_id=vote.id, candidate=candidate, rank=int(rank))
            db.session.add(pref)
        
        db.session.commit()
        
        # Convert preferences to the format expected by the template
        # Sort by rank (key) to ensure consistent ordering
        sorted_preferences = dict(sorted(preferences.items(), key=lambda x: int(x[0])))
        user_vote = {f"{k}. Preference": v for k, v in sorted_preferences.items()}
        return render_template('voted_confirmation.html', user_vote=user_vote)

    return render_template('vote.html', candidates=CANDIDATES, error=error)

# Admin routes
@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    if current_user.is_authenticated:
        return redirect(url_for('admin_dashboard'))
        
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        user = User.query.filter_by(username=username).first()
        
        if user and user.check_password(password) and user.is_admin:
            login_user(user)
            next_page = request.args.get('next')
            return redirect(next_page or url_for('admin_dashboard'))
        else:
            flash('Invalid username or password', 'error')
    
    return render_template('admin/login.html')

@app.route('/admin/logout')
@login_required
def admin_logout():
    logout_user()
    return redirect(url_for('admin_login'))

@app.route('/admin/dashboard')
@login_required
def admin_dashboard():
    if not current_user.is_authenticated or not current_user.is_admin:
        return redirect(url_for('admin_login'))
    
    # Get vote statistics
    total_votes = Vote.query.count()
    
    # Get first preference counts
    first_prefs = db.session.query(
        VotePreference.candidate,
        db.func.count(VotePreference.id).label('count')
    ).filter(VotePreference.rank == 1).group_by(VotePreference.candidate).all()
    
    # Prepare data for charts
    candidates = [pref[0] for pref in first_prefs]
    votes = [pref[1] for pref in first_prefs]
    
    # Get vote distribution by time
    votes_by_hour = db.session.query(
        db.func.strftime('%H', Vote.timestamp).label('hour'),
        db.func.count(Vote.id).label('count')
    ).group_by('hour').order_by('hour').all()
    
    hours = [f"{int(h[0])}:00" for h in votes_by_hour]
    votes_per_hour = [h[1] for h in votes_by_hour]
    
    return render_template('admin/dashboard.html',
                         total_votes=total_votes,
                         candidates=candidates,
                         votes=votes,
                         hours=hours,
                         votes_per_hour=votes_per_hour)

# API endpoint for getting vote distribution data
@app.route('/api/votes')
@login_required
def get_vote_data():
    prefs = db.session.query(
        VotePreference.candidate,
        VotePreference.rank,
        db.func.count(VotePreference.id).label('count')
    ).group_by(VotePreference.candidate, VotePreference.rank).all()
    
    # Format data for the frontend
    data = {}
    for candidate in CANDIDATES:
        data[candidate] = [0] * len(CANDIDATES)
    
    for pref in prefs:
        candidate, rank, count = pref
        if candidate in data and rank <= len(CANDIDATES):
            data[candidate][rank-1] = count
    
    return jsonify(data)

# API endpoint for getting recent votes
@app.route('/api/votes/recent')
@login_required
def get_recent_votes():
    # Get the 10 most recent votes with their preferences
    recent_votes = Vote.query.order_by(Vote.timestamp.desc()).limit(10).all()
    
    result = []
    for vote in recent_votes:
        prefs = VotePreference.query.filter_by(vote_id=vote.id)\
            .order_by(VotePreference.rank).all()
        
        result.append({
            'id': vote.id,
            'timestamp': vote.timestamp.isoformat(),
            'preferences': [{
                'candidate': pref.candidate,
                'rank': pref.rank
            } for pref in prefs]
        })
    
    return jsonify(result)

# Export vote results
@app.route('/admin/export/votes.<file_type>')
@login_required
def export_votes(file_type):
    if file_type not in ['csv', 'json']:
        return jsonify({'error': 'Invalid file type'}), 400
    
    # Get all votes with their preferences
    votes = Vote.query.order_by(Vote.timestamp).all()
    
    if file_type == 'csv':
        import csv
        from io import StringIO
        import csv
        from flask import make_response
        
        def generate():
            data = StringIO()
            writer = csv.writer(data)
            
            # Write header
            writer.writerow(['Vote ID', 'Timestamp'] + [f'Choice {i}' for i in range(1, len(CANDIDATES) + 1)])
            yield data.getvalue()
            data.seek(0)
            data.truncate(0)
            
            # Write vote data
            for vote in votes:
                prefs = {pref.rank: pref.candidate for pref in vote.preferences}
                row = [vote.id, vote.timestamp.strftime('%Y-%m-%d %H:%M:%S')]
                for i in range(1, len(CANDIDATES) + 1):
                    row.append(prefs.get(i, ''))
                writer.writerow(row)
                yield data.getvalue()
                data.seek(0)
                data.truncate(0)
        
        # Create a response with the CSV data
        response = make_response(generate())
        response.headers['Content-Type'] = 'text/csv'
        response.headers['Content-Disposition'] = f'attachment; filename=votes_export_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv'
        return response
    
    elif file_type == 'json':
        result = []
        for vote in votes:
            prefs = {pref.rank: pref.candidate for pref in vote.preferences}
            result.append({
                'id': vote.id,
                'timestamp': vote.timestamp.isoformat(),
                'preferences': [prefs.get(i, '') for i in range(1, len(CANDIDATES) + 1)]
            })
        
        response = jsonify({
            'metadata': {
                'generated_at': datetime.utcnow().isoformat(),
                'total_votes': len(votes),
                'candidates': CANDIDATES
            },
            'votes': result
        })
        
        return response

# Run the application
if __name__ == '__main__':
    # Get port from environment variable or default to 3000
    port = int(os.environ.get('PORT', 3000))
    # Only run with debug=True in development
    debug = os.environ.get('FLASK_ENV') == 'development'
    app.run(host='0.0.0.0', port=port, debug=debug)
