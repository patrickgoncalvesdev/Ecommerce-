from rest_framework import serializers
from ecommerce.models.modality import Modality
from ecommerce.serializers.placing import PlacingSerializer

class ModalitySerializer(serializers.ModelSerializer):
    placements = PlacingSerializer(many=True)
    
    class Meta:
        model = Modality
        exclude = ["ref"]
        
    def to_representation(self, instance):
        payload =  super().to_representation(instance)
        placements = payload.pop('placements')
        payload['placements'] = placements
        return payload