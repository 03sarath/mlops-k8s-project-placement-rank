import requests

candidate = [{"gender": "M",
  "ssc_p": 71.0,
  "ssc_b": 'Central',
  "hsc_p": 58.66,
  "hsc_b": 'Central',
  "hsc_s": 'Science',
  "degree_p": 58.0,
  "degree_t": 'Sci&Tech',
  "etest_p": 56.0,
  "mba_p": 61.3,
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
