from flask import Flask, request, jsonify
import time

app = Flask(__name__)
print('Flask - Creating app.')

# endpoints
@app.route('/test', methods=['GET'])
def test():
    print('Flask - /test endpoint.')
    msg = "App is running: " + time.ctime()
    return jsonify(response = msg)

if __name__ == '__main__':
    print('Flask - Running app.')
    app.run(debug=False, host='localhost', port=5000)