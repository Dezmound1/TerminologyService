from django.contrib import admin
from django.urls import reverse
from django.utils.html import format_html

from .models import Element, RefBook, Version


@admin.register(RefBook)
class RefBookAdmin(admin.ModelAdmin):
    list_display = ("id", "code", "name", "current_version", "start_date")
    search_fields = ("code", "name")
    ordering = ("code",)

    def current_version(self, obj):
        current = obj.versions.filter(
            start_date__lte=obj.versions.queryset.datetimes("start_date", "day").latest("start_date")
        ).first()
        if current:
            url = reverse("admin:refbooks_version_change", args=(current.id,))
            return format_html('<a href="{}">{}</a>', url, current.version)
        return "-"

    current_version.short_description = "Текущая версия"

    def start_date(self, obj):
        current = obj.versions.filter(
            start_date__lte=obj.versions.queryset.datetimes("start_date", "day").latest("start_date")
        ).first()
        return current.start_date if current else "-"

    start_date.short_description = "Дата начала версии"


@admin.register(Version)
class VersionAdmin(admin.ModelAdmin):
    list_display = ("id", "refbook_code", "refbook_name", "version", "start_date")
    list_filter = ("refbook", "start_date")
    search_fields = ("refbook__code", "refbook__name", "version")
    ordering = ("refbook__code", "start_date")

    def refbook_code(self, obj):
        return obj.refbook.code

    refbook_code.short_description = "Код справочника"

    def refbook_name(self, obj):
        return obj.refbook.name

    refbook_name.short_description = "Наименование справочника"


@admin.register(Element)
class ElementAdmin(admin.ModelAdmin):
    list_display = ("id", "version_refbook", "version_version", "code", "value")
    list_filter = ("version__refbook", "version__version")
    search_fields = ("version__refbook__code", "version__refbook__name", "code", "value")
    ordering = ("version__refbook__code", "version__version", "code")

    def version_refbook(self, obj):
        return obj.version.refbook.code

    version_refbook.short_description = "Справочник"

    def version_version(self, obj):
        return obj.version.version

    version_version.short_description = "Версия"
