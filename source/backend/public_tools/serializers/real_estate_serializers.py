# backend/public_tools/serializers/real_estate_serializers.py
from rest_framework import serializers
from decimal import Decimal

class SimulationRequestSerializer(serializers.Serializer):
    """
    Validation des demandes de simulation immobilière
    """
    property_price = serializers.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        min_value=Decimal('10000'),
        max_value=Decimal('10000000')
    )
    down_payment = serializers.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        min_value=Decimal('0')
    )
    loan_duration_years = serializers.IntegerField(
        min_value=1, 
        max_value=50
    )
    interest_rate = serializers.DecimalField(
        max_digits=5, 
        decimal_places=3, 
        min_value=Decimal('0.1'),
        max_value=Decimal('15.0')
    )
    
    def validate(self, data):
        """
        Validation croisée
        """
        if data['down_payment'] >= data['property_price']:
            raise serializers.ValidationError(
                "L'apport ne peut pas être supérieur ou égal au prix du bien"
            )
        
        return data