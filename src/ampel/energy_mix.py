from ampel import api

URL = 'https://thingspeak.umwelt-campus.de/channels/688'
RANGE = 8    


def get_sustainable_energy_distribution(hour: int):
    response = api.http_get_request(URL, f'/field/{hour + 1}/last.json')
    sustainable_energy_distribution = float(response[f'field{hour + 1}']) / 100
    return sustainable_energy_distribution
