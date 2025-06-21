import requests

candidate = [{"gender": "M",
  "ssc_p": 41.0,
  "ssc_b": 'Central',
  "hsc_p": 38.66,
  "hsc_b": 'Central',
  "hsc_s": 'Science',
  "degree_p": 28.0,
  "degree_t": 'Sci&Tech',
  "etest_p": 46.0,
  "mba_p": 31.3,
  "specialisation": 'Mkt&Fin',
  "workex": 'Yes',
  }]
url = "http://localhost:9696/predict"
response = requests.post(url=url, json=candidate)

if response.status_code == 200:
    output = response.json()
    print(f'Candidate features have been evaluated and output is {output}')
else:
    print(f'Error in evaluating features, status code: {response.status_code}')
