import sqlite3
import os
from dotenv import load_dotenv
import threading
import time

load_dotenv()

class Utils:
    def __init__(self):
        self.db_path = os.getenv('DATABASE_NAME')
        self.players_data = []
        self.update_interval = 3600  # Update interval in seconds (1 hour)
        self.update_thread = threading.Thread(target=self.update_player_list_periodically, daemon=True)
        self.update_thread.start()

    def get_db_connection(self):
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row  # To get dictionary-like row objects
        return conn

    def fetch_player_details(self, discord_id):
        conn =  self.get_db_connection()
        details = conn.execute('SELECT * FROM Player WHERE discordID = ?', (discord_id,)).fetchone()
        conn.close()
        return details
    
    def fetch_player_disc(self, player_id):
        conn = self.get_db_connection()
        id = conn.execute('SELECT discordID FROM Player WHERE playerID = ?', (player_id,)).fetchall()
        conn.close()
        return id[0]['discordID']  
    
    def fetch_players_paginated(self, offset, limit):
        conn = self.get_db_connection()
        players = conn.execute('SELECT discordID, playerID, winCount, lossCount, primaryRole, secondaryRole, ROUND(leaderboardPoints, 0) AS leaderboardPoints FROM Player ORDER BY leaderboardPoints DESC LIMIT ? OFFSET ?', (limit, offset)).fetchall()
        conn.close()
        return [dict(player) for player in players]
    
    def fetch_player_accounts(self, player_id):
        conn =  self.get_db_connection()
        accounts = conn.execute('SELECT * FROM account WHERE playerID = ?', (player_id,)).fetchall()
        conn.close()
        return [dict(acc) for acc in accounts]
    
    def fetch_player_profile(self, discord_id):
        conn =  self.get_db_connection()
        res =   conn.execute(f"""
                                  SELECT champion, SUM(kills), SUM(deaths), SUM(assists), count(champion) as Games, 
                                  SUM(CASE WHEN ratingChange > 0 THEN 1
								  ELSE 0
								  END) AS winCount,
								  SUM(CASE WHEN ratingChange < 0 THEN 1
								  ELSE 0
								  END) AS lossCount
                                  FROM PlayerMatch
                                  JOIN Player on Player.playerID = PlayerMatch.playerID
                                  JOIN Match on Match.matchID = PlayerMatch.matchID
                                  WHERE Player.discordID = '{discord_id}' and champion is not null AND (season = {0} OR {0} = 0)
                                  GROUP BY champion
                                  ORDER BY Games DESC, winCount DESC
                                  LIMIT 20
                                  """).fetchall()
        conn.close()
        return [dict(player) for player in res]
    
    def fetch_player_history(self, discord_id):
        conn = self.get_db_connection()
        matches = conn.execute(f"""
                                   SELECT   PlayerMatch.matchID, Match.matchTime, ROUND(PlayerMatch.ratingChange, 0) AS ratingChange, PlayerMatch.role,
                                            PlayerMatch.team, ifnull(PlayerMatch.champion, 'NA'), ifnull(PlayerMatch.kills, 'NA'), ifnull(PlayerMatch.deaths, 'NA'), ifnull(PlayerMatch.assists, 'NA')
                                   FROM PlayerMatch 
                                   JOIN Match on PlayerMatch.matchID = Match.matchID 
                                   JOIN Player on PlayerMatch.playerID = Player.playerID
                                   WHERE Player.discordID = {discord_id} AND season = 2
                                   ORDER BY Match.matchID desc
                                   LIMIT 10
                                   """).fetchall()
        conn.close()
        return [dict(match) for match in matches]
    
    def fetch_player_winstreak(self, player_id, mode):
        conn = self.get_db_connection()
        recent_games = conn.execute(
                f"SELECT ratingChange FROM PlayerMatch join Match on Match.matchID = PlayerMatch.matchID WHERE playerID = {player_id} and mode = '{mode.upper()}' ORDER BY PlayerMatchID desc LIMIT 3").fetchall()
        hotstreak = ""
        if len(recent_games) >= 3:
            hotstreak = True
            for game, in recent_games:
                if game <= 0:
                    hotstreak = False
        return hotstreak
    
    def fetch_player_rank(self, discord_id):
        conn = self.get_db_connection()
        # Fetch player's rank
        query = """
        SELECT (
            SELECT COUNT(*) + 1
            FROM Player AS p2
            WHERE p2.leaderboardPoints > p1.leaderboardPoints
            AND (p2.winCount > 0 OR p2.lossCount > 0)
        ) AS rank
        FROM Player AS p1
        WHERE discordID = ?
        """
        res = conn.execute(query, (discord_id,))
        rank = res.fetchone()
        return rank[0]
                    
    def fetch_betties(self, offset, limit):
        conn = self.get_db_connection()
        players = conn.execute('SELECT discordID, playerID, ROUND(bettingPoints, 0) AS bettingPoints FROM Player ORDER BY bettingPoints DESC LIMIT ? OFFSET ?', (limit, offset)).fetchall()
        conn.close()
        return [dict(player) for player in players]
    
    def update_player_list(self):
        conn = self.get_db_connection()
        players = conn.execute('SELECT playerID, discordID FROM Player').fetchall()
        conn.close()
        self.players_data = [dict(player) for player in players]

    def update_player_list_periodically(self):
        while True:
            self.update_player_list()
            time.sleep(self.update_interval)

# Example usage:
# utils = Utils()
# players = utils.fetch_players()
# paginated_players = utils.fetch_players_paginated(offset=0, limit=10)
# player_accounts = utils.fetch_player_accounts(player_id=1)