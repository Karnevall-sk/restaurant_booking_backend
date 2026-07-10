from rest_framework.permissions import BasePermission


class IsAdmin(BasePermission):
    def has_permission(self, request, view):
        return (
            request.user.is_authenticated
            and request.user.role == "admin"
        )


class IsManager(BasePermission):
    def has_permission(self, request, view):
        return (
            request.user.is_authenticated
            and request.user.role == "manager"
        )


class IsCustomer(BasePermission):
    def has_permission(self, request, view):
        return (
            request.user.is_authenticated
            and request.user.role == "customer"
        )

class IsReservationsOwner(BasePermission):
    def has_object_permission(self, request, view, obj):
        return obj.user == request.user

class CanCancelReservation(BasePermission):
    def has_object_permission(self, request, view, obj):
        user = request.user

        if user.role == "admin":
            return True

        if user.role == "manager":
            return obj.restaurant == user.restaurant

        return obj.user == user

class IsManagerOrAdmin(BasePermission):
    def has_permission(self, request, view):
        return (
            request.user.is_authenticated
            and request.user.role in ["manager", "admin"]
        )

class CanManageRestaurant(BasePermission):

    def has_object_permission(self, request, view, obj):
        if request.user.role == "admin":
            return True

        return (
            request.user.role == "manager"
            and obj == request.user.restaurant
        )