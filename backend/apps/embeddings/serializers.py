from rest_framework import serializers
from .models import SchemaEmbedding


class SchemaEmbeddingSerializer(serializers.ModelSerializer):
    class Meta:
        model = SchemaEmbedding
        fields = ['id', 'table_name', 'ddl_statement', 'description', 'embedding_id', 'created_at', 'updated_at']


class EmbedSchemaRequestSerializer(serializers.Serializer):
    table_name = serializers.CharField(max_length=255)
    ddl_statement = serializers.CharField()
    description = serializers.CharField(required=False, allow_blank=True)