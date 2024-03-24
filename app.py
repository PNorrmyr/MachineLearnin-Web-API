import token

from flask import Flask, request, jsonify, make_response
import jwt
import datetime
import pickle
from functools import wraps

app = Flask(__name__)
loaded_model = (pickle.load
                (open(r"C:\Users\Philip\Documents\Skola\Jupyter-notebook\PremiereLeague\final_model.sav", 'rb')))

app.config['SECRET_KEY'] = 'key'


def load_accuracy():
    accuracy = pickle.load(
        open(r"C:\Users\Philip\Documents\Skola\Jupyter-notebook\PremiereLeague\accuracy_score.pkl", 'rb'))
    return accuracy


def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.args.get('token')

        if not token:
            return jsonify(message="Missing token"), 401

        try:
            data = jwt.decode(token, app.config['SECRET_KEY'], algorithms=['HS256'])
        except:
            return jsonify({'message': 'Token is invalid'}), 403

        return f(*args, **kwargs)

    return decorated


@app.route('/api/v1/ml')
def unprotected():
    return jsonify({'message': 'Not protected'})


@app.route('/api/v1/ml/login')
def login():
    auth = request.authorization

    if auth and auth.password == 'tol':
        token = jwt.encode({'user': auth.username, 'exp': datetime.datetime.utcnow() + datetime.timedelta(minutes=30)},
                           app.config['SECRET_KEY'])

        return jsonify({'token': token})

    return make_response('Could not verify your access', 401, {'WWW-Authenticate': 'Basic realm="Login Required"'})


@app.route('/api/v1/ml/predict', methods=['POST'])
@token_required
def predict():
    half_time_home_team_goals = request.json.get('HalfTimeHomeTeamGoals')
    half_time_away_team_goals = request.json.get('HalfTimeAwayTeamGoals')
    home_team_corners = request.json.get('HomeTeamCorners')
    away_team_corners = request.json.get('AwayTeamCorners')
    home_team_fouls = request.json.get('HomeTeamFouls')
    away_team_fouls = request.json.get('AwayTeamFouls')
    home_team_yellow_cards = request.json.get('HomeTeamYellowCards')
    away_team_yellow_cards = request.json.get('AwayTeamYellowCards')
    home_team_red_cards = request.json.get('HomeTeamRedCards')
    away_team_red_cards = request.json.get('AwayTeamRedCards')

    prediction = loaded_model.predict([[half_time_home_team_goals, half_time_away_team_goals,
                                        home_team_corners, away_team_corners, home_team_fouls,
                                        away_team_fouls, home_team_yellow_cards, away_team_yellow_cards,
                                        home_team_red_cards, away_team_red_cards]])

    prediction = float(round(prediction[0], 2))

    prediction_mapping = {
        0: 'Draw',
        1: 'Home Team',
        2: 'Away Team'
    }
    converted_pred = prediction_mapping[prediction]

    output = {
        'Prediction': converted_pred,
        'Accuracy': load_accuracy()
    }

    return jsonify(output)


if __name__ == '__main__':
    app.run(debug=True)
