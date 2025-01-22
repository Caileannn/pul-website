# main.py
from flask import Flask, render_template, request, jsonify
from utils import Utils
from datetime import datetime

app = Flask(__name__, static_folder='static')
db_utils = Utils()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/bettyboard')
def bettyboard():
    return render_template('index.html')

# API endpoint to fetch players with pagination
@app.route('/api/players')
def get_players():
    offset = int(request.args.get('offset', 0))
    limit = int(request.args.get('limit', 20))
    players = db_utils.fetch_players_paginated(offset, limit)
    for player in players:
            hotstreak = db_utils.fetch_player_winstreak(player["playerID"], "SR")
            player["hotstreak"] = hotstreak
    return jsonify(players)

# API endpoint to fetch players with pagination
@app.route('/api/betties')
def get_betties():
    offset = int(request.args.get('offset', 0))
    limit = int(request.args.get('limit', 20))
    players = db_utils.fetch_betties(offset, limit)
    return jsonify(players)

@app.route('/player/<int:player_id>')
def player_detail(player_id):
    current_time = datetime.now()
    accounts = db_utils.fetch_player_accounts(player_id)
    disc_id = db_utils.fetch_player_disc(player_id)
    profile = db_utils.fetch_player_profile(disc_id)
    match_hisory = db_utils.fetch_player_history(disc_id)
    rank = db_utils.fetch_player_rank(disc_id)
    details = db_utils.fetch_player_details(disc_id)

    for match in match_hisory:
        match_time = datetime.strptime(match['matchTime'], '%Y-%m-%d %H:%M:%S.%f')
        time_since_match = current_time - match_time
        total_seconds = time_since_match.total_seconds()
        minutes = total_seconds // 60
        hours = minutes // 60
        days = hours // 24
        
        if minutes < 60:
            match['time_since_match'] = f"{int(minutes)} minutes ago"
        elif hours < 24:
            match['time_since_match'] = f"{int(hours)} hours ago"
        else:
            match['time_since_match'] = f"{int(days)} days ago"

    if accounts is None:
        return "Player not found!", 404
    return render_template('profile.html', profile=profile, accounts=accounts, history=match_hisory, id=disc_id, rank=rank, details=details)

@app.route('/search')
def search():
    query = request.args.get('q', '').lower()
    if not query:
        return jsonify([])

    # Try to convert query to integer for comparison
    try:
        query_int = int(query)
    except ValueError:
        return jsonify([])

    # Filter players in memory using integer comparison
    results = [player for player in db_utils.players_data if str(query_int) in str(player['discordID'])]
    return jsonify(results[:5])

if __name__ == '__main__':
    app.run(debug=True)