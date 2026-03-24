import pytest
import datetime
from unittest.mock import patch
from Backend.Backend_authlib import new_session, validate_session
from Backend.Backend_dblib import get_user_by_ID



def test_get_user_by_ID_valid():
    """Test: get_user_by_ID with valid integer ID returns user dict"""
    faux_user = [{"first_name": "Jane", "last_name": "Doe"}]
    with patch('Backend.Backend_dblib.execute_query', return_value=faux_user):
        result = get_user_by_ID(22)
        assert result == faux_user[0]
        assert isinstance(result, dict)

def test_get_user_by_ID_invalid_type():
    """Test: get_user_by_ID with string ID raises TypeError"""
    with pytest.raises(TypeError):
        get_user_by_ID("invalid_string")

def test_new_session_valid():
    """Test: new_session with valid parameters returns token string"""
    with patch('Backend.Backend_authlib.execute_query'):
        token = new_session(1, "192.168.254.111", "Mozilla/5.0")
        assert isinstance(token, str)
        assert len(token) > 32

def test_new_session_invalid_ip_type():
    """Test: new_session with integer IP raises TypeError"""
    with pytest.raises(TypeError):
        new_session(1, 4656, "Mozilla/5.0")


def test_validate_session_valid():
    """Test: Validate non-expired session returns True and correct user_id"""
    future_time = (datetime.datetime.now() + datetime.timedelta(hours=1)).strftime('%Y-%m-%d %H:%M:%S')
    session_data = [{"user_id": 1, "expire_time": future_time}]
    with patch('Backend.Backend_authlib.execute_query', return_value=session_data) as mock_execute_query:
        valid, user_id = validate_session("valid_token", "192.168.254.111")
        assert valid is True
        assert user_id == 1
        assert isinstance(valid, bool)
        assert isinstance(user_id, int)

def test_validate_session_expired():
    """Test: Expired session returns False"""
    past_time = (datetime.datetime.now() - datetime.timedelta(hours=1)).strftime('%Y-%m-%d %H:%M:%S')
    expired_session = [{"user_id": 1, "expire_time": past_time}]
    with patch('Backend.Backend_authlib.execute_query', return_value=expired_session):
        valid, user_id = validate_session("expired_token", "192.168.254.111")
        assert valid is False

def test_validate_session_none_token():
    """Test: validate_session with None token raises TypeError"""
    with pytest.raises(TypeError):
        validate_session(None, "192.168.254.111")