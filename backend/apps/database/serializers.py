from rest_framework import serializers


class QueryRequestSerializer(serializers.Serializer):
    query = serializers.CharField(max_length=5000)