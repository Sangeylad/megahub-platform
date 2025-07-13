# backend/tests/test_runners.py
"""
Script pour exécuter tous les tests avec différentes configurations
"""

import subprocess
import sys
import os

def run_all_tests():
    """Exécute tous les tests"""
    cmd = [
        'pytest', 
        'tests/',
        '-v',
        '--tb=short',
        '--disable-warnings'
    ]
    return subprocess.run(cmd)

def run_structure_tests():
    """Exécute seulement les tests de structure"""
    cmd = [
        'pytest', 
        'tests/test_billing_features_structure.py',
        'tests/test_core_business_structure.py',
        '-v'
    ]
    return subprocess.run(cmd)

def run_endpoints_tests():
    """Exécute seulement les tests d'endpoints"""
    cmd = [
        'pytest', 
        'tests/test_users_endpoints.py',
        'tests/test_company_brand_endpoints.py', 
        'tests/test_billing_endpoints.py',
        'tests/test_features_slots_endpoints.py',
        '-v',
        '-m', 'endpoints'
    ]
    return subprocess.run(cmd)

def run_billing_tests():
    """Exécute seulement les tests billing"""
    cmd = [
        'pytest', 
        'tests/test_billing_features_structure.py',
        'tests/test_billing_endpoints.py',
        '-v',
        '-m', 'billing'
    ]
    return subprocess.run(cmd)

def run_coverage_tests():
    """Exécute les tests avec coverage"""
    cmd = [
        'pytest', 
        'tests/',
        '--cov=.',
        '--cov-report=html',
        '--cov-report=term-missing',
        '-v'
    ]
    return subprocess.run(cmd)

def run_performance_tests():
    """Exécute les tests de performance"""
    cmd = [
        'pytest', 
        'tests/',
        '-v',
        '-m', 'slow',
        '--durations=10'
    ]
    return subprocess.run(cmd)

if __name__ == '__main__':
    if len(sys.argv) > 1:
        test_type = sys.argv[1]
        
        if test_type == 'structure':
            run_structure_tests()
        elif test_type == 'endpoints':
            run_endpoints_tests()
        elif test_type == 'billing':
            run_billing_tests()
        elif test_type == 'coverage':
            run_coverage_tests()
        elif test_type == 'performance':
            run_performance_tests()
        else:
            print("Types disponibles: structure, endpoints, billing, coverage, performance")
    else:
        run_all_tests()

# ============================================================================

# Makefile pour faciliter l'exécution
"""
# Makefile

.PHONY: test test-structure test-endpoints test-billing test-coverage test-fast

# Tests complets
test:
	pytest tests/ -v --tb=short --disable-warnings

# Tests de structure seulement  
test-structure:
	pytest tests/test_billing_features_structure.py tests/test_core_business_structure.py -v

# Tests d'endpoints seulement
test-endpoints:
	pytest tests/test_*_endpoints.py -v

# Tests billing seulement
test-billing:
	pytest tests/test_billing_features_structure.py tests/test_billing_endpoints.py -v

# Tests avec coverage
test-coverage:
	pytest tests/ --cov=. --cov-report=html --cov-report=term-missing -v

# Tests rapides (skip slow)
test-fast:
	pytest tests/ -v -m "not slow"

# Tests par catégorie
test-users:
	pytest tests/test_users_endpoints.py -v

test-companies:
	pytest tests/test_company_brand_endpoints.py::CompanyEndpointsTestCase -v

test-brands:
	pytest tests/test_company_brand_endpoints.py::BrandEndpointsTestCase -v

test-features:
	pytest tests/test_features_slots_endpoints.py -v

test-permissions:
	pytest tests/ -v -k "permissions"

# Setup et nettoyage
setup-test-db:
	python manage.py migrate --settings=backend.settings_test

clean-test:
	find . -name "*.pyc" -delete
	find . -name "__pycache__" -delete
	rm -rf htmlcov/
	rm -f .coverage

# Installation des dépendances de test
install-test-deps:
	pip install pytest pytest-django pytest-cov factory-boy

# Lancer tous les tests avec rapport détaillé
test-full-report:
	pytest tests/ -v --tb=long --cov=. --cov-report=html --cov-report=term-missing --durations=20
"""