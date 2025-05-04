from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route('/pay', methods=['POST'])
def process_payment():
    data = request.json
    amount = data.get('amount')
    user = data.get('user')

    if amount and user:
        return jsonify({'status': 'success', 'message': f'Payment of ${amount} by {user} received.'})
    return jsonify({'status': 'error', 'message': 'Invalid data'}), 400

if __name__ == 'main':
    app.run(debug=True)
