from iati.factory import iati_factory
from api.activity import serializers


class TestActivitySerializers:

    def test_DefaultAidTypeSerializer(self):
        aidtype = iati_factory.AidTypeFactory.build(
            code=10,
        )
        s = serializers.DefaultAidTypeSerializer(aidtype)
        assert s.data['code'] == aidtype.code
