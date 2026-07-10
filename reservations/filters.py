from django_filters import rest_framework as filters
from .models import Reservation

class ReservationFilter(filters.FilterSet):
 
    date = filters.DateFilter(
        field_name="start_time",
        lookup_expr="date",
    )
    
    date_from = filters.DateFilter(
        field_name="start_time",
        lookup_expr="date__gte",
    )

    date_to = filters.DateFilter(
        field_name="start_time",
        lookup_expr="date__lte",
    )

    class Meta:
        model = Reservation
        fields = {
            "status": ["exact"],
            "restaurant": ["exact"],
            "customer_phone": ["exact"],
            "user": ["exact"]
        }