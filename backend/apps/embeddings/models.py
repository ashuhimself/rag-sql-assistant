from django.db import models


class SchemaEmbedding(models.Model):
    table_name = models.CharField(max_length=255)
    ddl_statement = models.TextField()
    description = models.TextField(blank=True)
    embedding_id = models.CharField(max_length=255, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['table_name']

    def __str__(self):
        return f"Schema: {self.table_name}"