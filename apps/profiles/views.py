from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView

from .exceptions import ProfileNotFound, NotYourProfile
from .models import Profile
from .renderers import ProfileJSONRenderer
from .serializers import ProfileSerializer, UpdateProfileSerializer

# Create your views here.
# We will use class based views instead of function based views
# Study the difference and Ref : https://www.django-rest-framework.org/api-guide/views/#class-based-views
# Study function based views : https://www.django-rest-framework.org/api-guide/views/#function-based-views

class AgentListAPIView(generics.ListAPIView):
    permission_classes = [permissions.IsAuthenticated]
    queryset = Profile.objects.filter(is_agent=True)
    serializer_class = ProfileSerializer

    # Ref : https://www.django-rest-framework.org/api-guide/requests/#get
    def get_queryset(self):
        user = self.request.user
        queryset = Profile.objects.filter(user=user)
        return queryset
    
    
class TopAgentsListAPIView(generics.ListAPIView):
    permission_classes = [permissions.IsAuthenticated]
    queryset = Profile.objects.filter(top_agent=True)
    serializer_class = ProfileSerializer


class GetProfileAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    renderer_classes = [ProfileJSONRenderer]
    serializer_class = ProfileSerializer

    # Ref : https://www.django-rest-framework.org/api-guide/requests/#get
    def get(self, request):
        user = self.request.user
        user_profile = Profile.objects.get(user=user)
        serializer =  ProfileSerializer(user_profile, context={"request": request})
        return Response(serializer.data, status=status.HTTP_200_OK)


class UpdateProfileAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    renderer_classes = [ProfileJSONRenderer]
    serializer_class = UpdateProfileSerializer

    # Ref : https://www.django-rest-framework.org/api-guide/requests/#patch
    def patch(self, request, username):
        try:
            Profile.objects.get(user__username=username)
        except Profile.DoesNotExist:
            raise ProfileNotFound

        user_name = request.user.username
        if user_name != username:
            raise NotYourProfile

        data = request.data
        serializer = UpdateProfileSerializer(
            instance=request.user.profile, data=data, partial=True
        )

        serializer.is_valid()
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)