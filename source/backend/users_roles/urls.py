# backend/users_roles/urls.py

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from users_roles.views.roles_views import RoleViewSet, PermissionViewSet, UserRoleViewSet

# ✅ Routers séparés pour éviter les conflits
roles_router = DefaultRouter()
roles_router.register(r'', RoleViewSet, basename='role')

permissions_router = DefaultRouter() 
permissions_router.register(r'', PermissionViewSet, basename='permission')

user_roles_router = DefaultRouter()
user_roles_router.register(r'', UserRoleViewSet, basename='user-role')

urlpatterns = [
    # Chaque router a son préfixe
    path('roles/', include(roles_router.urls)),           # /users/roles/
    path('permissions/', include(permissions_router.urls)), # /users/permissions/
    path('user-roles/', include(user_roles_router.urls)),  # /users/user-roles/
]