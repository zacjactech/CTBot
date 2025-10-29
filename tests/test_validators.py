import pytest
from src.bot.validators import validate_and_normalize_order_params

@pytest.fixture
def mock_filters():
    return {
        "filters": [
            {"filterType": "PRICE_FILTER", "tickSize": "0.01"},
            {"filterType": "LOT_SIZE", "stepSize": "0.001", "minQty": "0.001"},
        ]
    }

def test_valid_params(mock_filters):
    params = {"price": 123.456, "quantity": 1.2345}
    result = validate_and_normalize_order_params(params, mock_filters)
    assert result["price"] == 123.46
    assert result["quantity"] == 1.234

def test_quantity_too_low(mock_filters):
    params = {"quantity": 0.0001}
    with pytest.raises(ValueError):
        validate_and_normalize_order_params(params, mock_filters)
