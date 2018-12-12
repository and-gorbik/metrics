import requests

class Asteroid:
    BASE_API_URL = 'https://api.nasa.gov/neo/rest/v1/neo/{}?api_key=DEMO_KEY'

    def __init__(self, spk_id):
        self.api_url = self.BASE_API_URL.format(spk_id)
    
    def get_data(self):
        return requests.get(self.api_url).json()
    
    @property
    def name(self):
        return self.get_data()['name']

    @property
    def diameter(self):
        return int(self.get_data()['estimated_diameter']['meters']['estimated_diameter_max'])

if __name__ == "__main__":
    import json

    a = Asteroid(2099942)
    with open("apophis_fixture.txt", "w") as f:
        f.write(json.dumps(a.get_data()))