from django.contrib import admin
from .models import GardenPlot
from .models import VolunteerEvent
from .models import CropRecord
from .models import Analytics

@admin.register(Analytics)
class AnalyticsAdmin(admin.ModelAdmin):
    list_display = ('user', 'action', 'timestamp', 'details')
    list_filter = ('action', 'timestamp')
    search_fields = ('user__username', 'details')

admin.site.register(GardenPlot)
admin.site.register(VolunteerEvent)
admin.site.register(CropRecord)