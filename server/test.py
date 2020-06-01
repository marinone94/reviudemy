import json
import requests

def main():
    response = requests.get('http://localhost:5000/test')
    print(json.loads(response.text))
    print('Test successful.')

if __name__ == '__main__':
    main()