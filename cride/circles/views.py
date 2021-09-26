"""circles views"""

# django rest framework
from rest_framework.decorators import api_view
from rest_framework.response import Response

# django
from cride.circles.models import Circle

from cride.circles.serializers import (CircleSerializers,CreateCircleSerializer)

@api_view(['GET'])
def list_circles(request):
    """list circles"""
    circles = Circle.objects.filter(is_public=True)
    # serializers transform data query sets django models to python data and then to JSON, XML
    serializer = CircleSerializers(circles,many=True)
    return Response(serializer.data)

@api_view(['POST'])
def create_circle(request):
    serializer = CreateCircleSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    circle = serializer.save()
    return Response(CircleSerializers(circle).data)

