from rest_framework import serializers
from .models import CustomUser

class CustomerSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = [
            'id', 
            'name', 
            'email', 
            'mobile_number', 
            'address', 
            'id_proof',  
            'id_proof_number',  # Include the new field here
            'photo', 
            'created_at', 
            'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']  # These fields are read-only

from rest_framework import serializers
from .models import Job

class JobSerializer(serializers.ModelSerializer):
    class Meta:
        model = Job
        fields = ['id', 'name']
        read_only_fields = ['id']  
