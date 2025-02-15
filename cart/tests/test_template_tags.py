import pytest
from decimal import Decimal
from django.template import Template, Context
from cart.templatetags.cart_tags import multiply

class TestCartTemplateTags:
    def test_multiply_integers(self):
        """Test multiply filter with integers"""
        assert multiply(5, 3) == 15.0
        assert multiply('5', 3) == 15.0

    def test_multiply_decimals(self):
        """Test multiply filter with decimals"""
        assert multiply(Decimal('10.50'), 2) == 21.0
        assert multiply('10.50', 2) == 21.0

    def test_multiply_zero(self):
        """Test multiply filter with zero"""
        assert multiply(5, 0) == 0.0
        assert multiply(0, 5) == 0.0
        assert multiply('0', 5) == 0.0

    def test_multiply_negative(self):
        """Test multiply filter with negative numbers"""
        assert multiply(5, -2) == -10.0
        assert multiply(-5, 2) == -10.0
        assert multiply('-5', 2) == -10.0

    def test_multiply_filter_in_template(self):
        """Test multiply filter in a template"""
        template = Template(
            '{% load cart_tags %}'
            '{{ value|multiply:multiplier }}'
        )
        context = Context({'value': '10.50', 'multiplier': 2})
        result = template.render(context)
        assert float(result) == 21.0

    def test_multiply_invalid_value(self):
        """Test multiply filter with invalid value"""
        with pytest.raises(ValueError):
            multiply('invalid', 2)

    def test_multiply_none_value(self):
        """Test multiply filter with None value"""
        assert multiply(None, 2) == 0.0 