"""
Test runners and utilities for the AutoCusto test suite.

Provides custom test runners and utilities for running different test categories.
"""

import os
import sys
from django.test.runner import DiscoverRunner
from django.conf import settings


class SessionFunctionalityTestRunner(DiscoverRunner):
    """Test runner for session functionality tests only."""
    
    def setup_test_environment(self, **kwargs):
        super().setup_test_environment(**kwargs)
        settings.TEST_RUNNER_TYPE = 'session_functionality'
    
    def get_test_modules(self):
        """Return only session functionality test modules."""
        return [
            'tests.session_functionality.test_crm_cns_functionality',
            'tests.session_functionality.test_setup_flow',
        ]


class IntegrationTestRunner(DiscoverRunner):
    """Test runner for integration tests only."""
    
    def setup_test_environment(self, **kwargs):
        super().setup_test_environment(**kwargs)
        settings.TEST_RUNNER_TYPE = 'integration'
    
    def get_test_modules(self):
        """Return only integration test modules."""
        return [
            'tests.integration.test_clinic_setup',
            'tests.integration.test_process_setup',
        ]


class FormTestRunner(DiscoverRunner):
    """Test runner for form tests only."""
    
    def setup_test_environment(self, **kwargs):
        super().setup_test_environment(**kwargs)
        settings.TEST_RUNNER_TYPE = 'forms'
    
    def get_test_modules(self):
        """Return only form test modules."""
        return [
            'tests.forms.test_medico_forms',
        ]


class ViewTestRunner(DiscoverRunner):
    """Test runner for view tests only."""
    
    def setup_test_environment(self, **kwargs):
        super().setup_test_environment(**kwargs)
        settings.TEST_RUNNER_TYPE = 'views'
    
    def get_test_modules(self):
        """Return only view test modules."""
        return [
            'tests.views.test_medico_views',
        ]


class CentralizedTestRunner(DiscoverRunner):
    """Test runner that uses the centralized test structure."""
    
    def setup_test_environment(self, **kwargs):
        super().setup_test_environment(**kwargs)
        settings.TEST_RUNNER_TYPE = 'centralized'
    
    def get_test_modules(self):
        """Return all centralized test modules."""
        return [
            # Session functionality tests
            'tests.session_functionality.test_crm_cns_functionality',
            'tests.session_functionality.test_setup_flow',
            # Integration tests
            'tests.integration.test_clinic_setup',
            'tests.integration.test_process_setup',
            # Form tests
            'tests.forms.test_medico_forms',
            # View tests
            'tests.views.test_medico_views',
        ]


def run_session_tests():
    """Helper function to run only session functionality tests."""
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'autocusto.settings')
    from django.core.management import execute_from_command_line
    
    execute_from_command_line([
        'manage.py', 'test',
        'tests.session_functionality',
        '--settings=test_settings'
    ])


def run_integration_tests():
    """Helper function to run only integration tests."""
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'autocusto.settings')
    from django.core.management import execute_from_command_line
    
    execute_from_command_line([
        'manage.py', 'test',
        'tests.integration',
        '--settings=test_settings'
    ])


def run_form_tests():
    """Helper function to run only form tests."""
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'autocusto.settings')
    from django.core.management import execute_from_command_line
    
    execute_from_command_line([
        'manage.py', 'test',
        'tests.forms',
        '--settings=test_settings'
    ])


def run_view_tests():
    """Helper function to run only view tests."""
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'autocusto.settings')
    from django.core.management import execute_from_command_line
    
    execute_from_command_line([
        'manage.py', 'test',
        'tests.views',
        '--settings=test_settings'
    ])


def run_all_centralized_tests():
    """Helper function to run all centralized tests."""
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'autocusto.settings')
    from django.core.management import execute_from_command_line
    
    execute_from_command_line([
        'manage.py', 'test',
        'tests',
        '--settings=test_settings'
    ])


if __name__ == '__main__':
    """Command line interface for running specific test categories."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Run AutoCusto tests by category')
    parser.add_argument('category', choices=[
        'session', 'integration', 'forms', 'views', 'all'
    ], help='Test category to run')
    
    args = parser.parse_args()
    
    if args.category == 'session':
        run_session_tests()
    elif args.category == 'integration':
        run_integration_tests()
    elif args.category == 'forms':
        run_form_tests()
    elif args.category == 'views':
        run_view_tests()
    elif args.category == 'all':
        run_all_centralized_tests()
