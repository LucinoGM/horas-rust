import unittest
from unittest.mock import patch

from rust_hours_server import app, set_api_enabled


class FakeResponse:
    def __init__(self, payload):
        self._payload = payload

    def json(self):
        return self._payload


class ApiToggleTests(unittest.TestCase):
    def setUp(self):
        app.config['TESTING'] = True
        self.client = app.test_client()
        set_api_enabled(True)

    def test_toggle_endpoint_switches_state(self):
        response = self.client.post('/api/toggle-status')

        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertFalse(data['enabled'])
        self.assertEqual(data['message'], 'API desligada')

    def test_status_endpoint_reports_disabled_state(self):
        toggle_response = self.client.post('/api/toggle-status')
        self.assertEqual(toggle_response.status_code, 200)

        response = self.client.get('/api/status')

        self.assertEqual(response.status_code, 503)
        data = response.get_json()
        self.assertFalse(data['online'])
        self.assertFalse(data['enabled'])
        self.assertIn('desligada', data['error'].lower())

    def test_rust_hours_endpoint_is_disabled_when_api_is_off(self):
        self.client.post('/api/toggle-status')

        response = self.client.get('/rust-hours')

        self.assertEqual(response.status_code, 503)
        self.assertIn('desligada', response.get_data(as_text=True).lower())

    def test_status_endpoint_includes_analytics_payload(self):
        with patch('rust_hours_server.requests.get', side_effect=[
            FakeResponse({'response': {'games': [{'appid': 252490, 'playtime_forever': 6000, 'name': 'Rust'}]}}),
            FakeResponse({'response': {'players': [{'personaname': 'Tester', 'avatarfull': 'http://avatar', 'personastate': 1, 'gameextrainfo': 'Rust', 'gameid': '252490'}]}})
        ]):
            response = self.client.get('/api/status')

        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertIn('analytics', data)
        self.assertIn('chart', data['analytics'])
        self.assertIn('ranking', data['analytics'])
        self.assertIn('calendar', data['analytics'])

    def test_status_endpoint_ranks_friends(self):
        with patch('rust_hours_server.requests.get', side_effect=[
            FakeResponse({'response': {'games': [{'appid': 252490, 'playtime_forever': 6000, 'name': 'Rust'}]}}),
            FakeResponse({'response': {'players': [{'personaname': 'Tester', 'avatarfull': 'http://avatar', 'personastate': 1, 'gameextrainfo': 'Rust', 'gameid': '252490'}]}}),
            FakeResponse({'friendslist': {'friends': [{'steamid': '1001'}, {'steamid': '1002'}]}}),
            FakeResponse({'response': {'players': [
                {'steamid': '1001', 'personaname': 'Friend One', 'avatarfull': 'http://friend1', 'personastate': 1},
                {'steamid': '1002', 'personaname': 'Friend Two', 'avatarfull': 'http://friend2', 'personastate': 0}
            ]}}),
            FakeResponse({'response': {'games': [{'appid': 252490, 'playtime_forever': 1200, 'name': 'Rust'}]}}),
            FakeResponse({'response': {'games': [{'appid': 252490, 'playtime_forever': 2400, 'name': 'Rust'}]}})
        ]):
            response = self.client.get('/api/status')

        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        ranking_names = [entry['name'] for entry in data['analytics']['ranking']]
        self.assertIn('Friend One', ranking_names)
        self.assertIn('Friend Two', ranking_names)

    def test_status_endpoint_returns_analytics_when_rust_missing(self):
        with patch('rust_hours_server.requests.get', side_effect=[
            FakeResponse({'response': {'games': [{'appid': 999999, 'playtime_forever': 100, 'name': 'Other Game'}]}}),
            FakeResponse({'response': {'players': [{'personaname': 'Tester', 'avatarfull': 'http://avatar', 'personastate': 1}]}}),
            FakeResponse({'friendslist': {'friends': [{'steamid': '1001'}]}}),
            FakeResponse({'response': {'players': [{'steamid': '1001', 'personaname': 'Friend One', 'avatarfull': 'http://friend1', 'personastate': 1}]}}),
            FakeResponse({'response': {'games': []}})
        ]):
            response = self.client.get('/api/status')

        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertIn('analytics', data)
        self.assertTrue(any(entry['name'] == 'Friend One' for entry in data['analytics']['ranking']))


if __name__ == '__main__':
    unittest.main()
