import tweepy
import requests
import time
from datetime import datetime, time as dt_time

# Clés API Twitter
API_KEY = '4Z9ujGB2WsXhisbmPb6BbOdip'
API_KEY_SECRET = 'iRYbHbFB1dQLbUj0hoKqTU8RpGce902cw6k3cPsOO0UIEBYXu2'
ACCESS_TOKEN = '1826287656134746112-JmG85BGXOLb9ZUIpziufIEuPfAxCHy'
ACCESS_TOKEN_SECRET = 'VKiL8XZd9Sb7y901B82KS7A7yB16lWcPhskQFa9TwSAdo'
BEARER_TOKEN = 'AAAAAAAAAAAAAAAAAAAAAGwkvgEAAAAAL16PJphW8ZD8OTsYo%2FDWVS25X9E%3DDZvInyN0AImpxwYmfINwOj7RuRx46IMi5HdBIBfNMtSADYSvi6'

# Clé API-Football
API_FOOTBALL_KEY = '2fa9c9dc762813cb02ea4f97642cd104'

# Liste des ligues que tu veux suivre
LEAGUES_TO_FOLLOW = {
    'Ligue 1': (61, '🇫🇷'),         # France
    'Premier League': (39, '🏴'),  # England
    'Serie A': (135, '🇮🇹'),        # Italy
    'La Liga': (140, '🇪🇸'),        # Spain
    'Bundesliga': (78, '🇩🇪')       # Germany
}

# Configuration du client Tweepy avec l'API v2
client = tweepy.Client(
    bearer_token=BEARER_TOKEN,
    consumer_key=API_KEY,
    consumer_secret=API_KEY_SECRET,
    access_token=ACCESS_TOKEN,
    access_token_secret=ACCESS_TOKEN_SECRET
)

last_tweet_content = None

def test_authentication():
    """
    Teste l'authentification avec l'API Twitter v2.
    """
    try:
        response = client.get_me()
        if response.data:
            print(f"Authentification réussie ! Utilisateur connecté : {response.data.username}")
        else:
            print("Erreur lors de l'authentification.")
    except tweepy.TweepyException as e:
        print(f"Erreur d'authentification : {e}")

def fetch_completed_matches():
    """
    Récupère les résultats des matchs terminés pour les ligues spécifiées, incluant la date et l'heure.
    """
    url = "https://v3.football.api-sports.io/fixtures"
    headers = {'x-apisports-key': API_FOOTBALL_KEY}
    matches = []
    
    for league_name, (league_id, country_emoji) in LEAGUES_TO_FOLLOW.items():
        params = {
            'league': league_id,
            'season': 2023,  # Utiliser l'année courante pour la saison actuelle
            'status': 'FT'   # Récupérer uniquement les matchs terminés
        }
        response = requests.get(url, headers=headers, params=params)
        data = response.json()

        if data['response']:
            for match in data['response']:
                home_team = match['teams']['home']['name']
                away_team = match['teams']['away']['name']
                home_score = match['goals']['home']
                away_score = match['goals']['away']
                match_date = match['fixture']['date']
                matches.append((league_name, country_emoji, home_team, away_team, home_score, away_score, match_date))
    
    return matches

def format_datetime(datetime_str):
    """
    Formatte la date et l'heure de l'API-Football pour les afficher dans un tweet.
    """
    dt = datetime.fromisoformat(datetime_str.replace('Z', '+00:00'))
    return dt.strftime('%d %B %Y, %H:%M')

def generate_hashtag(name):
    """
    Génère un hashtag à partir du nom de l'équipe ou de la ligue.
    """
    return '#' + name.replace(' ', '')

def get_team_emoji(team_name):
    """
    Renvoie l'emoji correspondant à l'équipe, s'il existe.
    """
    team_emojis = {
        # Ligue 1
        'Angers': '⚫⚪',
        'Auxerre': '🔵⚪',
        'Brest': '🔴⚪',
        'Le Havre': '🔵⚪',
        'Lens': '🟡🔴',
        'Lille': '🔴⚪',
        'Lyon': '🔴🔵⚪',
        'Marseille': '⚪🔵',
        'Monaco': '⚪🔴',
        'Montpellier': '🔵🟠',
        'Nantes': '🟡🟢',
        'Nice': '🔴⚫',
        'Paris SG': '🗼🔵🔴',
        'Reims': '⚪🔴',
        'Rennes': '🔴⚫',
        'Saint-Étienne': '🟢⚪',
        'Strasbourg': '🔵⚪',
        'Toulouse': '🟣⚪',
        
        # La Liga
        'Alavès': '🔵⚪',
        'Athletic Bilbao': '🔴⚪',
        'Atletico Madrid': '🔴⚪🔵',
        'Barcelone': '🔵🔴',
        'Betis Séville': '🟢⚪',
        'Celta Vigo': '🔵⚪',
        'Espanyol': '🔵⚪',
        'FC Séville': '⚪🔴',
        'Getafe': '🔵⚪',
        'Girona': '⚪🔴',
        'Las Palmas': '🟡🔵',
        'Leganes': '🟢⚪',
        'Majorque': '⚫🔴',
        'Osasuna': '🔴🔵',
        'Rayo Vallecano': '🔴⚪',
        'Real Madrid': '⚪👑',
        'Real Sociedad': '🔵⚪',
        'Real Valladolid': '🟣⚪',
        'Valence': '⚫🟠',
        'Villarreal': '🟡⚪',
        
        # Bundesliga
        'Augsburg': '⚪🔴',
        'Bayern Munich': '🔴⚪',
        'Bochum': '🔵⚪',
        'Dortmund': '🟡⚫',
        'Francfort': '⚫⚪',
        'Fribourg': '🔴⚪',
        'Heidenheim': '🔴⚪',
        'Hoffenheim': '🔵⚪',
        'Kiel': '⚪🔵',
        'Leipzig': '⚪🔴',
        'Leverkusen': '⚫🔴',
        'Mayence': '🔴⚪',
        'Mönchengladbach': '⚪⚫',
        'St. Pauli': '🟤⚪',
        'Stuttgart': '⚪🔴',
        'Union Berlin': '🔴⚪',
        'Werder Bremen': '🟢⚪',
        'Wolfsburg': '🟢⚪',
        
        # Premier League
        'Arsenal': '🔴🔫',
        'Aston Villa': '🟣🔵',
        'Bournemouth': '⚫🔴',
        'Brentford': '🔴⚪',
        'Brighton': '🔵⚪',
        'Chelsea': '🔵🦁',
        'Crystal Palace': '🔴🔵🦅',
        'Everton': '🔵⚪',
        'Fulham': '⚫⚪',
        'Ipswich Town': '🔵⚪',
        'Leicester': '🔵⚪',
        'Liverpool': '🔴🐦',
        'Manchester City': '🔵⚪',
        'Manchester United': '🔴⚪',
        'Newcastle': '⚫⚪',
        'Nottingham Forest': '🔴🌳',
        'Southampton': '🔴⚪',
        'Tottenham': '⚪🐓',
        'West Ham': '⚒️',
        'Wolverhampton': '🟠⚫🐺',
        

        # Serie A
        'As Rome': '🟠🔴',
        'Bergame (Atalanta)': '🔵⚫',
        'Bologne': '🔴🔵',
        'Cagliari': '🔴🔵',
        'Côme': '🔵⚪',
        'Empoli': '🔵⚪',
        'Fiorentina': '🟣⚪',
        'Genoa': '🔴🔵',
        'Hellas Vérone': '🔵🟡',
        'Inter Milan': '🔵⚫',
        'Juventus Turin': '⚫⚪',
        'Lazio Rome': '🟦⚪',
        'Lecce': '🔴🟡',
        'Milan AC': '🔴⚫',
        'Monza': '⚪🔴',
        'Naples': '🔵⚪',
        'Parme': '🟡🔵',
        'Torino': '🟤⚪',
        'Udinese': '⚫⚪',
        'Venise (Venezia)': '⚫🟢🟠'
    }
    return team_emojis.get(team_name, '')

def post_tweet(content):
    """
    Publie un tweet avec le contenu donné en utilisant l'API v2.
    Vérifie si le tweet est un doublon avant de le publier.
    """
    global last_tweet_content
    if content == last_tweet_content:
        print("Tweet en doublon détecté, publication ignorée.")
        return
    
    try:
        response = client.create_tweet(text=content)
        if response.data:
            last_tweet_content = content
            print(f"Tweet publié avec succès ! ID du tweet : {response.data['id']}")
        else:
            print("Erreur lors de la publication du tweet.")
    except tweepy.TweepyException as e:
        if e.response and e.response.status_code == 429:
            print("Erreur 429 : Trop de requêtes. Pause et réessayer...")
            time.sleep(60)  # Attendre 60 secondes avant de réessayer
            post_tweet(content)
        else:
            print(f"Erreur lors de la publication du tweet : {e}")

def tweet_completed_matches():
    """
    Publie les résultats des matchs terminés pour les ligues spécifiées avec la date, l'heure et les emojis.
    """
    current_time = datetime.now().time()
    if current_time < dt_time(13, 0) or current_time > dt_time(23, 15):
        print("Hors de la plage des heures de match, script suspendu.")
        return
    
    matches = fetch_completed_matches()
    if matches:
        for match in matches:
            league, country_emoji, home_team, away_team, home_score, away_score, match_date = match
            formatted_date = format_datetime(match_date)
            league_hashtag = generate_hashtag(league)
            home_team_hashtag = generate_hashtag(home_team)
            away_team_hashtag = generate_hashtag(away_team)
            home_team_emoji = get_team_emoji(home_team)
            away_team_emoji = get_team_emoji(away_team)
            
            tweet_content = (f"{country_emoji} {league}: {home_team_emoji} {home_team} {home_score} - {away_score} {away_team_emoji} {away_team} | {formatted_date} "
                             f"{league_hashtag} {home_team_hashtag} {away_team_hashtag} "
                             f"#Football #MatchTerminé")
            post_tweet(tweet_content)
            
            time.sleep(900)  # Pause de 15 minutes entre chaque requête pour économiser les requêtes API
    else:
        print("Aucun match terminé trouvé.")

# Tester l'authentification
test_authentication()

# Publier les résultats des matchs terminés
tweet_completed_matches()
