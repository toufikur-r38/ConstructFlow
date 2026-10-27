import os
import unittest
from types import SimpleNamespace
from unittest.mock import patch

os.environ.setdefault('FLASK_ENV', 'development')
os.environ.setdefault('SECRET_KEY', 'test-secret-key')

from flask import Flask
from werkzeug.datastructures import MultiDict
from app.modules.construction.routes import costs


class CostGridValidationTest(unittest.TestCase):
    def setUp(self):
        self.app = Flask(__name__)
        self.app.secret_key = 'test'

    def submit(self, data):
        with self.app.test_request_context('/add-cost', method='POST', data=MultiDict(data),
                                           headers={'X-Cost-Grid': '1'}):
            with patch.object(costs, 'db') as database, patch.object(costs, 'get_dropdown_options', return_value=['Materials']):
                database.session.get.return_value = SimpleNamespace(id=1, is_void=False, status='Running')
                response, status = costs._save_cost_rows()
                database.session.commit.assert_not_called()
                return response.get_json(), status

    def test_reports_all_invalid_rows_using_original_serial_numbers(self):
        result, status = self.submit([
            ('project_id', '1'),
            ('date[]', ''), ('date[]', 'bad-date'), ('date[]', '2026-01-01'),
            ('cost_type[]', ''), ('cost_type[]', 'Materials'), ('cost_type[]', 'Unknown'),
            ('quantity[]', ''), ('quantity[]', 'NaN'), ('quantity[]', '1'),
            ('unit_rate[]', ''), ('unit_rate[]', '5'), ('unit_rate[]', ''),
        ])
        self.assertEqual(status, 422)
        self.assertEqual(set(result['errors']), {'2', '3'})
        self.assertIn('Expense date', ' '.join(result['errors']['2']))
        self.assertIn('Quantity', ' '.join(result['errors']['2']))
        self.assertIn('Category', ' '.join(result['errors']['3']))
        self.assertIn('Unit rate is required', ' '.join(result['errors']['3']))

    def test_blank_date_defaults_to_today_and_negative_values_require_remarks(self):
        result, status = self.submit([
            ('project_id', '1'), ('date[]', ''), ('cost_type[]', 'Materials'),
            ('quantity[]', '-2'), ('unit_rate[]', '-5'), ('remarks[]', ''),
        ])
        self.assertEqual(status, 422)
        reasons = ' '.join(result['errors']['1'])
        self.assertIn('Remarks are required', reasons)
        self.assertIn('negative quantity or unit rate', reasons)
        self.assertNotIn('Expense date', reasons)

    def test_future_date_requires_remarks(self):
        result, status = self.submit([
            ('project_id', '1'), ('date[]', '9999-01-01'), ('cost_type[]', 'Materials'),
            ('quantity[]', '2'), ('unit_rate[]', '5'), ('remarks[]', ''),
        ])
        self.assertEqual(status, 422)
        self.assertIn('future expense date', ' '.join(result['errors']['1']))

    def test_rejects_oversized_submission_without_saving(self):
        result, status = self.submit([('project_id', '1')] + [('date[]', '')] * 21)
        self.assertEqual(status, 400)
        self.assertIn('21', result['errors'])

    def test_empty_submission_identifies_first_row(self):
        result, status = self.submit([('project_id', '1'), ('date[]', '')])
        self.assertEqual(status, 422)
        self.assertIn('1', result['errors'])


if __name__ == '__main__':
    unittest.main()
