from datetime import datetime

from rest_framework import viewsets
from rest_framework import generics

from call.models import Call, Bill
from call.api.serializers import CallSerializer, BillSerializer


class CallViewSet(viewsets.GenericViewSet, generics.ListCreateAPIView, generics.RetrieveAPIView):
    queryset = Call.objects.all()
    serializer_class = CallSerializer


class BillViewSet(generics.ListAPIView):
    serializer_class = BillSerializer

    def get_queryset(self):
        # the call_number needs to be the number that originated the call
        call_number = self.kwargs.get('destination')
        month = self.kwargs.get('month', datetime.now().month - 1)
        year = self.kwargs.get('year', datetime.now().year)

        return Bill.objects.filter(destination__source=call_number, year=year, month=month)
