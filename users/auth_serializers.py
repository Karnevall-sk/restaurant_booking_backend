from rest_framework_simplejwt.serializers import TokenObtainPairSerializer


class PhoneTokenObtainPairSerializer(TokenObtainPairSerializer):

    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)

        token["role"] = user.role

        return token

    def validate(self, attrs):
        data = super().validate(attrs)

        data["user"] = {
            "id": self.user.id,
            "phone": str(self.user.phone),
            "role": self.user.role,
            "name": self.user.name,
        }

        return data