import logging

import django_filters
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import QuerySet
from rest_framework import filters, generics, permissions, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.views import APIView

from .exceptions import PropertyNotFound
from .models import Property
from .pagination import PropertyPagination
from .serializers import (PropertyCreateSerializer, PropertySerializer,
                          PropertyViews, PropertyViewSerializer)

logger = logging.getLogger(__name__)


class PropertyFilter(django_filters.FilterSet):
    # Ref : https://www.django-rest-framework.org/api-guide/filtering/#django-filters-filterset
    advert_type = django_filters.CharFilter(
        field_name="advert_type", lookup_expr="iexact"
    )
    property_type = django_filters.CharFilter(
        field_name="property_type",
        lookup_expr="iexact",
    )
    price = django_filters.NumberFilter()
    price__gt = django_filters.NumberFilter(field_name="price", lookup_expr="gt")
    price__lt = django_filters.NumberFilter(field_name="price", lookup_expr="lt")

    class Meta:
        model = Property
        fields = ["advert_type", "property_type", "price"]


class ListAllPropertiesAPIView(generics.ListAPIView):
    serializer_class = PropertySerializer
    queryset = Property.objects.all().order_by("-created_at")
    pagination_class = PropertyPagination
    # Ref : https://www.django-rest-framework.org/api-guide/filtering/#django-filters-filterset
    filter_backends = [
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter,
    ]

    filterset_class = PropertyFilter
    search_fields = ["country", "city"]
    ordering_fields = ["created_at"]


class ListAgentsPropertiesAPIView(generics.ListAPIView):
    serializer_class = PropertySerializer
    pagination_class = PropertyPagination
    filter_backends = [
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter,
    ]

    filterset_class = PropertyFilter
    search_fields = ["country", "city"]
    ordering_fields = ["created_at"]

    def get_queryset(self) -> QuerySet:
        user = self.request.user
        queryset = Property.objects.filter(user=user).order_by("-created_at")
        return queryset


class PropertyViewsAPIView(generics.ListAPIView):
    serializer_class = PropertyViewSerializer
    queryset = PropertyViews.objects.all()


class PropertyDetailAPIView(APIView):
    # Track property views by IP address to prevent duplicate counting
    def get(self, request, slug):
        property_obj = Property.objects.get(slug=slug)

        x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
        if x_forwarded_for:
            ip = x_forwarded_for.split(",")[0]
        else:
            ip = request.META.get("REMOTE_ADDR")

        if not PropertyViews.objects.filter(property=property_obj, ip=ip).exists():
            PropertyViews.objects.create(property=property_obj, ip=ip)
            property_obj.views += 1
            property_obj.save()

        serializer = PropertySerializer(property_obj, context={"request": request})

        return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(["PUT"])
@permission_classes([permissions.IsAuthenticated])
def update_property_api_view(request, slug):
    # Function-based view for updating property
    try:
        property_obj = Property.objects.get(slug=slug)
    except Property.DoesNotExist:
        raise PropertyNotFound

    user = request.user
    if property_obj.user != user:
        return Response(
            {"error": "You cannot update a property that doesn't belong to you"},
            status=status.HTTP_403_FORBIDDEN,
        )
    if request.method == "PUT":
        data = request.data
        serializer = PropertySerializer(property_obj, data, many=False)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(["POST"])
@permission_classes([permissions.IsAuthenticated])
def create_property_api_view(request):
    user = request.user
    data = request.data
    data["user"] = request.user.pkid
    serializer = PropertyCreateSerializer(data=data)

    if serializer.is_valid():
        serializer.save()
        logger.info(
            f"property {serializer.data.get('title')} created by {user.username}"
        )
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(["DELETE"])
@permission_classes([permissions.IsAuthenticated])
def delete_property_api_view(request, slug):
    try:
        property_obj = Property.objects.get(slug=slug)
    except Property.DoesNotExist:
        raise PropertyNotFound

    user = request.user
    if property_obj.user != user:
        return Response(
            {"error": "You cannot delete a property that doesn't belong to you"},
            status=status.HTTP_403_FORBIDDEN,
        )
    if request.method == "DELETE":
        delete_operation = property_obj.delete()
        data = {}
        if delete_operation:
            data["success"] = "Deletion was successful"
        else:
            data["failure"] = "Deletion failed"
        return Response(data=data, status=status.HTTP_204_NO_CONTENT)


@api_view(["POST"])
@permission_classes([permissions.IsAuthenticated])
def upload_property_image(request):
    data = request.data

    property_id = data["property_id"]
    property_obj = Property.objects.get(id=property_id)

    property_obj.cover_photo = request.FILES.get("cover_photo")
    property_obj.photo1 = request.FILES.get("photo1")
    property_obj.photo2 = request.FILES.get("photo2")
    property_obj.photo3 = request.FILES.get("photo3")
    property_obj.photo4 = request.FILES.get("photo4")

    property_obj.save()

    return Response({"success": "Images uploaded successfully"}, status=status.HTTP_200_OK)


class PropertySearchAPIView(generics.GenericAPIView):
    """Advanced property search with multiple filters."""

    permission_classes = [permissions.AllowAny]
    serializer_class = PropertySerializer

    def get_queryset(self) -> QuerySet:
        """Return published properties for search."""
        return Property.objects.filter(published_status=True)

    def post(self, request):
        """
        Execute property search with filters.

        POST /api/v1/properties/search/

        Request body:
        {
            "advert_type": "For Sale",
            "property_type": "House",
            "price": "₹41,50,000+",
            "bedrooms": "2+",
            "bathrooms": "1+",
            "catch_phrase": "oceanview"
        }
        """
        queryset = self.get_queryset()
        data = request.data

        if "advert_type" in data:
            advert_type = data["advert_type"]
            queryset = queryset.filter(advert_type__iexact=advert_type)

        if "property_type" in data:
            property_type = data["property_type"]
            queryset = queryset.filter(property_type__iexact=property_type)

        # Price filtering in INR (Indian Rupees)
        price = data.get("price", "Any")
        price_map = {
            "₹0+": 0,
            "₹41,50,000+": 4150000,
            "₹83,00,000+": 8300000,
            "₹1,66,00,000+": 16600000,
            "₹41,50,00,000+": 415000000,
            "₹49,80,00,000+": 49800000,
            "Any": -1,
        }
        price_value = price_map.get(price, -1)

        if price_value != -1:
            queryset = queryset.filter(price__gte=price_value)

        # Filter by minimum bedrooms
        bedrooms = data.get("bedrooms", "0+")
        bedroom_map = {"0+": 0, "1+": 1, "2+": 2, "3+": 3, "4+": 4, "5+": 5}
        bedroom_value = bedroom_map.get(bedrooms, 0)
        queryset = queryset.filter(bedrooms__gte=bedroom_value)

        # Filter by minimum bathrooms
        bathrooms = data.get("bathrooms", "0+")
        bathroom_map = {
            "0+": 0.0, "1+": 1.0, "2+": 2.0, "3+": 3.0, "4+": 4.0
        }
        bathroom_value = bathroom_map.get(bathrooms, 0.0)
        queryset = queryset.filter(bathrooms__gte=bathroom_value)

        # Search in property description
        catch_phrase = data.get("catch_phrase", "")
        if catch_phrase:
            queryset = queryset.filter(description__icontains=catch_phrase)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
