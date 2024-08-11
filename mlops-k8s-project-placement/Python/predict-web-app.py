from flask import Flask, jsonify
import requests

app = Flask(__name__)

@app.route('/')
def index():
    return '''
        <html>
            <body>
                <form action='/predict' method='post'>
                    <input type='submit' value='Invoke endpoint' id='predict_button'>
                </form>
                <script>
                    document.getElementById("predict_button").onclick = function () {
                        location.href = '/predict';
                    };
                </script>
            </body>
        </html>
    '''


@app.route('/predict', methods=['POST', 'GET'])

def predict():
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
    url = "http://127.0.0.1:65433/predict"
    response = requests.post(url=url, json=candidate)

    if response.status_code == 200:
        output = response.json()
        return jsonify(output)
    else:
        return jsonify({'error': f'Error in evaluating features, status code: {response.status_code}'})

if __name__ == '__main__':
    app.run(debug=True)
