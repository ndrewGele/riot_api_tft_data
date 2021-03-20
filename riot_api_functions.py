def get_league_summoner_ids(api_key, league = 'challenger', wait = 2):
  
  import requests
  import time
  
  # From highest to lowest:
  # challenger
  # grandmaster
  # master

  res = requests.get(
    f'https://na1.api.riotgames.com/tft/league/v1/{league}',
    headers = {
      'X-Riot-Token': api_key
    }
  ).json()

  res = [entry['summonerId'] for entry in res['entries']]
  
  time.sleep(wait)

  return(res)



def get_summoner_puuids(api_key, summoners, wait = 2):
  
  import requests
  import time 

  res = []

  for summoner in summoners:
    res.append(
      requests.get(
        f'https://na1.api.riotgames.com/tft/summoner/v1/summoners/{summoner}',
        headers = {
          'X-Riot-Token': api_key
        }
      ).json()['puuid']
    )

    time.sleep(wait)
  
  return(res)



def get_puuid_matches(api_key, puuids, count = 5, wait = 2):
  
  import requests
  import time 

  res = []

  for puuid in puuids:
    res.extend(
      requests.get(
        f'https://americas.api.riotgames.com/tft/match/v1/matches/by-puuid/{puuid}/ids',
        headers = {
          'X-Riot-Token': api_key
        },
        params = {
          'count': count
        }
      ).json()
    )

    time.sleep(wait)

  return(res)



def get_match_results(api_key, match_ids, wait = 2):
  
  import requests
  import time 

  res = []

  for match_id in match_ids:
    res.append(
      requests.get(
        f'https://americas.api.riotgames.com/tft/match/v1/matches/{match_id}',
        headers = {
          'X-Riot-Token': api_key
        }
      ).json()
    )

    time.sleep(wait)

  return(res)
