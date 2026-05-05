from django.contrib import admin
from django.utils import timezone

from .models import Element, RefBook, Version


class VersionInline(admin.TabularInline):
    model = Version
    extra = 0
    fields = ("version", "start_date")
    show_change_link = True


class ElementInline(admin.TabularInline):
    model = Element
    extra = 1
    fields = ("code", "value")


@admin.register(RefBook)
class RefBookAdmin(admin.ModelAdmin):
    list_display = ("id", "code", "name", "current_version", "current_version_start_date")
    search_fields = ("code", "name")
    ordering = ("code",)
    inlines = [VersionInline]

    def _current_version(self, obj: RefBook) -> Version | None:
        return (
            obj.versions
            .filter(start_date__lte=timezone.localdate())
            .order_by("-start_date")
            .first()
        )

    @admin.display(description="Текущая версия")
    def current_version(self, obj: RefBook) -> str:
        v = self._current_version(obj)
        return v.version if v else "—"

    @admin.display(description="Дата начала действия версии")
    def current_version_start_date(self, obj: RefBook) -> str:
        v = self._current_version(obj)
        return v.start_date.isoformat() if v else "—"


@admin.register(Version)
class VersionAdmin(admin.ModelAdmin):
    list_display = ("id", "refbook_code", "refbook_name", "version", "start_date")
    list_select_related = ("refbook",)
    list_filter = ("refbook", "start_date")
    search_fields = ("refbook__code", "refbook__name", "version")
    ordering = ("refbook__code", "start_date")
    inlines = [ElementInline]

    @admin.display(description="Код справочника", ordering="refbook__code")
    def refbook_code(self, obj: Version) -> str:
        return obj.refbook.code

    @admin.display(description="Наименование справочника", ordering="refbook__name")
    def refbook_name(self, obj: Version) -> str:
        return obj.refbook.name


@admin.register(Element)
class ElementAdmin(admin.ModelAdmin):
    list_display = ("id", "version_refbook", "version_version", "code", "value")
    list_select_related = ("version", "version__refbook")
    list_filter = ("version__refbook", "version__version")
    search_fields = ("version__refbook__code", "version__refbook__name", "code", "value")
    ordering = ("version__refbook__code", "version__version", "code")

    @admin.display(description="Справочник", ordering="version__refbook__code")
    def version_refbook(self, obj: Element) -> str:
        return obj.version.refbook.code

    @admin.display(description="Версия", ordering="version__version")
    def version_version(self, obj: Element) -> str:
        return obj.version.version
