import pytest
from app.config.settings import get_config, DevelopmentConfig, ProductionConfig, TestingConfig
import os
from unittest.mock import patch

def test_get_config_development():
    config = get_config("development")
    assert isinstance(config, DevelopmentConfig)
    assert config.ENV_NAME == "development"

def test_get_config_production():
    with patch.dict(os.environ, {"SECRET_KEY": "prod-key"}):
        config = get_config("production")
        assert isinstance(config, ProductionConfig)
        assert config.ENV_NAME == "production"

def test_get_config_testing():
    config = get_config("testing")
    assert isinstance(config, TestingConfig)
    assert config.ENV_NAME == "testing"

def test_get_config_invalid():
    with pytest.raises(ValueError, match="Unknown configuration: 'invalid'"):
        get_config("invalid")

def test_get_config_default():
    with patch.dict(os.environ, {"FLASK_ENV": "development"}):
        config = get_config()
        assert isinstance(config, DevelopmentConfig)

def test_production_missing_secret_key():
    with patch.dict(os.environ, {}, clear=True):
        with pytest.raises(ValueError, match="SECRET_KEY environment variable is required in production"):
            get_config("production")
