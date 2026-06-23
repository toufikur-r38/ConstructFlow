import unittest
import os
from datetime import date
from decimal import Decimal
from io import BytesIO
from types import SimpleNamespace

from openpyxl import load_workbook

os.environ.setdefault('FLASK_ENV', 'development')
os.environ.setdefault('SECRET_KEY', 'test-secret-key')

from app.modules.construction.routes.costs import ALL_PROJECTS_FILTER, _has_export_filter
from app.modules.construction.utils.generate_costs_excel import generate_costs_excel
from app.modules.construction.utils.project_sorting import sort_projects_by_status_then_name


class ConstructionExportRulesTest(unittest.TestCase):
    def test_broad_project_filters_alone_do_not_allow_export(self):
        self.assertFalse(_has_export_filter('', '', '', ''))
        self.assertFalse(_has_export_filter(ALL_PROJECTS_FILTER, '', '', ''))

    def test_specific_project_or_detail_filter_allows_export(self):
        self.assertTrue(_has_export_filter('12', '', '', ''))
        self.assertTrue(_has_export_filter('', 'Materials', '', ''))
        self.assertTrue(_has_export_filter('', '', '2026-01-01', ''))
        self.assertTrue(_has_export_filter('', '', '', '2026-01-31'))

    def test_project_sorting_prioritizes_running_then_completed_then_on_hold(self):
        projects = [
            SimpleNamespace(project_name='Zeta', status='Completed'),
            SimpleNamespace(project_name='Beta', status='Running'),
            SimpleNamespace(project_name='Alpha', status='On Hold'),
            SimpleNamespace(project_name='Alpha', status='Running'),
        ]

        sorted_projects = sort_projects_by_status_then_name(projects)

        self.assertEqual(
            [(project.project_name, project.status) for project in sorted_projects],
            [
                ('Alpha', 'Running'),
                ('Beta', 'Running'),
                ('Zeta', 'Completed'),
                ('Alpha', 'On Hold'),
            ],
        )

    def test_excel_export_includes_sort_metadata_and_print_header_row(self):
        rows = [
            SimpleNamespace(
                date=date(2026, 1, 1),
                project=SimpleNamespace(project_name='Pagination Test Project'),
                project_id=1,
                cost_type='Materials',
                quantity=Decimal('2'),
                unit_rate=Decimal('100'),
                total_amount=Decimal('200'),
                remarks='First row',
            ),
        ]

        workbook_bytes = generate_costs_excel(rows, cost_type_filter='Materials')
        workbook = load_workbook(BytesIO(workbook_bytes), read_only=False)
        sheet = workbook['Cost Ledger']

        self.assertEqual(sheet.freeze_panes, 'A7')
        self.assertEqual(sheet.print_title_rows, '$6:$6')
        self.assertEqual(sheet.auto_filter.ref, 'A6:H6')
        self.assertIn('Sort Order: Date ascending, then Entry ID ascending', sheet['A5'].value)
        self.assertEqual(sheet['A6'].value, 'SL')
        self.assertEqual(sheet['C6'].value, 'Project')


if __name__ == '__main__':
    unittest.main()
