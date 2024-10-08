from django.contrib.auth import get_user_model
from rest_framework import permissions, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response

from apps.profiles.models import Profile
from .models import Rating

User = get_user_model()


@api_view(["POST"])
@permission_classes([permissions.IsAuthenticated])
def create_agent_review(request, profile_id):
    agent_profile = Profile.objects.get(id=profile_id, is_agent=True)
    data = request.data
    
    profile_user = User.objects.get(pkid = agent_profile.user.pkid)
    if profile_user.email == request.user.email:
        formatted_response = {
            "message": "You can't rate yourself"
        }
        return Response(formatted_response, status=status.HTTP_403_FORBIDDEN)
    
    alreadyExists = agent_profile.agent_review.filter(agent__pkid = profile_user.pkid).exists()

    if alreadyExists:
        formatted_response = {
            "details": "You have already rated this agent"
        }
        return Response(formatted_response, status=status.HTTP_403_FORBIDDEN)
    
    elif data["rating"] == 0:
        formatted_response = {
            "details": "Please select a rating"
        }
        return Response(formatted_response, status=status.HTTP_400_BAD_REQUEST)
    
    else:
        review = Rating.objects.create(
            rater = request.user,
            agent = agent_profile,
            rating = data["rating"],
            comment = data["comment"],
        )
        reviews = agent_profile.agent_review.all()
        agent_profile.num_reviews = len(reviews) + 1
        
        total = 0
        for i in reviews:   
            total += i.rating
            
        review.save()
        # We keep the formatted response as it is to follow later we will change it 
        formatted_response = {
            "details": "Review added successfully"
        }
        return Response("Review added successfully")
    