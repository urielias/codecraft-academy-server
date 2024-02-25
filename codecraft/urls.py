from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    # Admin site URLs
    path('admin/', admin.site.urls),

    # User management URLs
    path('users/', include('users.urls')),

    # Course management URLs
    path('courses/', include('courses.urls')),

    # Communications URLs
    path('comms/', include('communications.urls'))
]
