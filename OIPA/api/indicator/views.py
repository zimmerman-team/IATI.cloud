from api.indicator.serializers import IndicatorDataSerializer
from indicator.models import IndicatorData
from rest_framework.generics import ListAPIView


class IndicatorList(ListAPIView):
    queryset = IndicatorData.objects.all()
    serializer_class = IndicatorDataSerializer
