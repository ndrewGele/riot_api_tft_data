import os
import config
import riot_api_functions as api
import random
import re
from collections import Counter
from google.cloud import firestore


# Google cloud stuff

# Google auth
os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = './google_auth.json'

# Connect to db
db = firestore.Client()

# Get list of match ID's already obtained
docs = db.collection('match_results').stream()
already_have = [doc.id for doc in docs]


# Init the top leagues
leagues = ['challenger', 'grandmaster', 'master']


# Empty list for parsed api responses
parsed = []


# Loop through leagues
for league in leagues:

  # Fetch summoner ID's for top leagues
  players = api.get_league_summoner_ids(api_key = config.api_key, league = league)
  print(f'{len(players)} players found in {league} league.')
  players = random.choices(players, k = 3)
  
  # Fetch puuids to use in next api calls
  puuids = api.get_summoner_puuids(api_key = config.api_key, summoners = players)
  
  # Fetch match ID's
  matches = api.get_puuid_matches(api_key = config.api_key, puuids = puuids, count = 25)
  # Filter match ID's
  matches = [match for match in matches if match not in already_have]
  # Skip loop if all matches are already in db
  if len(matches) == 0:
    continue

  # Fetch match results
  results = api.get_match_results(api_key = config.api_key, match_ids = matches)
  
  i = 0
  for result in results:
    
    i += 1
    print(f'Parsing {i} result of {len(results)} in {league.title()} league.')
    
    participants = result.get('info').get('participants')
    for participant in participants:
      row = {
        'match_id': result.get('metadata').get('match_id'),
        'game_ver': re.search('\w{3} \d+ \d+\/\d+:\d+:\d+', result.get('info').get('game_version')).group(0),
        'league': league,
        'player_id': participant.get('puuid'),
        'placement': participant.get('placement'),
        'level': participant.get('level'),
        'num_units': len(participant.get('units'))
      }
      
      # Count FONs
      row['num_fons'] = row['num_units'] - row['level']
      
      # Get individual item counts
      combined_items = [item for unit in participant.get('units') for item in unit.get('items') if item < 100]
      individual_items = [component for item in combined_items for component in str(item)]
      for item, amount in Counter(individual_items).items():
        row[f'item_{item}'] = amount
      
      if 'item_8' in row:
        row['item_8'] = row['item_8'] + (row['num_fons'] * 2)
      
      # Get Units per trait
      for trait in participant.get('traits'):
        row[f'trait_{trait.get("name")}'] = f'{trait.get("num_units")}'
      
      parsed.append(row)


# Write to Firestore
for result in parsed:
  doc_id = result['match_id'] + '_' + str(result['placement'])
  doc_ref = db.collection('match_results').document(doc_id)
  doc_ref.set(result)