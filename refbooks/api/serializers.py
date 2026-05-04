from rest_framework import serializers

from refbooks.domain.entities import ElementEntity, RefBookEntity


class RefBookSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    code = serializers.CharField(max_length=100)
    name = serializers.CharField(max_length=300)

    @classmethod
    def from_entity(cls, entity: RefBookEntity) -> dict:
        return cls(
            {
                "id": entity.id,
                "code": entity.code,
                "name": entity.name,
            }
        ).data


class ElementSerializer(serializers.Serializer):
    code = serializers.CharField(max_length=100)
    value = serializers.CharField(max_length=300)

    @classmethod
    def from_entity(cls, entity: ElementEntity) -> dict:
        return cls(
            {
                "code": entity.code,
                "value": entity.value,
            }
        ).data


class CheckElementResponseSerializer(serializers.Serializer):
    exists = serializers.BooleanField()
