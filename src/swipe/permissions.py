from rest_framework.permissions import BasePermission


class IsDeveloper(BasePermission):
    '''Allows access only for developers'''

    def has_permission(self, request, view):
        is_developer = request.user and request.user.user_developer is not None 
        return is_developer


# class IsAdmin(BasePermission):
#     '''Allows access only for admin'''

#     def has_permission(self, request, view):
#         is_developer = request.user and request.user.user_developer is not None 
#         return is_developer