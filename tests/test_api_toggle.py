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


if __name__ == '__main__':
    unittest.main()
