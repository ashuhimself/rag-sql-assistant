import pytest
import os
import django
from django.conf import settings
from django.test.utils import get_runner
from unittest.mock import patch, Mock


def pytest_configure():
    settings.configure(
        DEBUG_PROPAGATE_EXCEPTIONS=True,
        DATABASES={
            'default': {
                'ENGINE': 'django.db.backends.sqlite3',
                'NAME': ':memory:',
            }
        },
        SITE_ID=1,
        SECRET_KEY='test-secret-key',
        USE_I18N=True,
        USE_L10N=True,
        STATIC_URL='/static/',
        ROOT_URLCONF='config.urls',
        INSTALLED_APPS=[
            'django.contrib.auth',
            'django.contrib.contenttypes',
            'django.contrib.sessions',
            'django.contrib.sites',
            'django.contrib.messages',
            'django.contrib.staticfiles',
            'rest_framework',
            'apps.chat',
            'apps.embeddings',
            'apps.database',
        ],
        MIDDLEWARE=[
            'django.middleware.security.SecurityMiddleware',
            'django.contrib.sessions.middleware.SessionMiddleware',
            'django.middleware.common.CommonMiddleware',
            'django.middleware.csrf.CsrfViewMiddleware',
            'django.contrib.auth.middleware.AuthenticationMiddleware',
            'django.contrib.messages.middleware.MessageMiddleware',
        ],
        REST_FRAMEWORK={
            'DEFAULT_PERMISSION_CLASSES': [
                'rest_framework.permissions.AllowAny',
            ],
        },
        QDRANT_URL='http://localhost:6333',
        OLLAMA_URL='http://localhost:11434',
        OLLAMA_MODEL='test-model',
        SQL_QUERY_TIMEOUT=30,
        MAX_RESULT_ROWS=1000,
    )
    django.setup()


@pytest.fixture
def mock_ollama_client():
    with patch('utils.ollama_client.OllamaClient') as mock:
        mock_instance = Mock()
        mock_instance.generate_sql.return_value = "SELECT * FROM customers LIMIT 10;"
        mock_instance.generate_response.return_value = "Found 10 customers in the database."
        mock_instance.generate_brief_response.return_value = "I can help with database queries."
        mock_instance.test_connection.return_value = {'success': True, 'message': 'Connected'}
        mock.return_value = mock_instance
        yield mock_instance


@pytest.fixture
def mock_qdrant_client():
    with patch('qdrant_client.QdrantClient') as mock:
        mock_instance = Mock()
        mock_instance.search.return_value = [
            Mock(
                payload={
                    'table_name': 'customers',
                    'ddl_statement': 'CREATE TABLE customers (id INT, name VARCHAR(100));',
                    'description': 'Customer information'
                },
                score=0.9
            )
        ]
        mock.return_value = mock_instance
        yield mock_instance


@pytest.fixture
def mock_sentence_transformer():
    with patch('sentence_transformers.SentenceTransformer') as mock:
        mock_instance = Mock()
        mock_instance.encode.return_value = [0.1] * 384  # Mock embedding
        mock.return_value = mock_instance
        yield mock_instance