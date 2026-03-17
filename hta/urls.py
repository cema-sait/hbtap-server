from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.http import JsonResponse
from django.db import connection
import signal


def health_check(request):
    db_config = settings.DATABASES.get("default", {})

    # Attempt DB connection with timeout
    def timeout_handler(signum, frame):
        raise TimeoutError("Database connection timeout")
    
    db_status = "ok"
    db_error = None
    
    try:
        # Set a 3-second timeout for the DB check
        signal.signal(signal.SIGALRM, timeout_handler)
        signal.alarm(3)
        
        connection.ensure_connection()
        
        signal.alarm(0)  # Cancel the alarm
    except TimeoutError as e:
        db_status = "error"
        db_error = "Database connection timeout"
    except Exception as e:
        db_status = "error"
        db_error = str(e)
    finally:
        signal.alarm(0)  # Ensure alarm is cancelled

    payload = {
        "status": "ok" if db_status == "ok" else "degraded",
        "debug": settings.DEBUG,
        "database": {
            "status": db_status,
            "engine": str(db_config.get("ENGINE", "unknown")),
            "name": str(db_config.get("NAME", "unknown")),
            "host": str(db_config.get("HOST", "unknown")),
            "port": str(db_config.get("PORT", "unknown")),
        },
    }

    if db_error:
        payload["database"]["error"] = db_error

    status_code = 200 if db_status == "ok" else 503
    return JsonResponse(payload, status=status_code)


urlpatterns = [
    path('api/health/', health_check, name='health-check'),
    path('api/admin/', admin.site.urls),
    path('api/v1/', include('users.urls')),
    path('api/v2/', include('members.urls')),
    path('api/v3/', include('app.urls')),
]
if settings.DEBUG:
    urlpatterns += staticfiles_urlpatterns()
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    
