from django.contrib import admin
from django.db.models import Count, Sum
from django.utils import timezone
from datetime import timedelta

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
                ).aggregate(Sum('total_price'))['total_price__sum'] or 0,
            }
        except:
            pass
        return response 