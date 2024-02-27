from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    # User management URLs
    path('', include('users.urls')),

    # Admin site URLs
    path('admin/', admin.site.urls),

    # Course management URLs
    path('courses/', include('courses.urls')),

    # Communications URLs
    path('comms/', include('communications.urls'))
]
