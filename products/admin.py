from django.contrib import admin
from django.db.models import Count, Sum
from django.utils import timezone
from datetime import timedelta
from .models import Category, Controller

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug']
    prepopulated_fields = {'slug': ('name',)}

class MonitoringAdmin(admin.ModelAdmin):
    change_list_template = 'admin/monitoring_change_list.html'

    def changelist_view(self, request, extra_context=None):
        response = super().changelist_view(request, extra_context=extra_context)
        
        try:
            qs = self.get_queryset(request)
            
            # Last 24 hours stats
            today = timezone.now()
            yesterday = today - timedelta(days=1)
            response.context_data['summary'] = {
                'total': qs.count(),
                'last_24h': qs.filter(created_at__range=(yesterday, today)).count(),
                'revenue_24h': qs.filter(
                    created_at__range=(yesterday, today)
                ).aggregate(Sum('price'))['price__sum'] or 0,
            }
        except Exception:
            pass
        return response

@admin.register(Controller)
class ControllerAdmin(MonitoringAdmin):
    list_display = ['name', 'slug', 'price', 'available', 'created_at', 'updated_at']
    list_filter = ['available', 'created_at', 'updated_at']
    list_editable = ['price', 'available']
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ['name', 'description']
    date_hierarchy = 'created_at'
    ordering = ['name'] 