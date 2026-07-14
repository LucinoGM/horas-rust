import unittest
from unittest.mock import patch

from rust_hours_server import app, set_api_enabled


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

        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertFalse(data['online'])
        self.assertFalse(data['enabled'])
        self.assertIn('desligada', data['error'].lower())


if __name__ == '__main__':
    unittest.main()
