from django.contrib import admin
from .models import (
    Theme,
    SetId,
    Images,
    SetInfo,
    Sellers,
)
from django.utils.html import format_html

@admin.register(Theme)
class ThemeAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "parent",
        "source",
    )
    list_filter = ("source",)
    search_fields = ("name",)
    ordering = ("parent__name", "name")


class ImagesInline(admin.TabularInline):
    model = Images
    extra = 0


class SellersInline(admin.TabularInline):
    model = Sellers
    extra = 0
    readonly_fields = ("source",)


@admin.register(SetId)
class SetIdAdmin(admin.ModelAdmin):
    list_display = (
        "set_id",
    )

@admin.register(SetInfo)
class SetInfoAdmin(admin.ModelAdmin):
    list_display = (
        "display_name",
        "set",
        "year",
        "parts",
        "weight",
        "dim",
    )

    search_fields = (
        "bricklink_name",
        "lego_name",
        "brickeconomy_name",
        "set__set_id",
    )

    list_filter = ("year",)

    fieldsets = (
        ("Names", {
            "fields": (
                "set",
                "bricklink_name",
                "lego_name",
                "brickeconomy_name",
                "bricksandminifigsanaheim_name",
            )
        }),
        ("Details", {
            "fields": (
                "year",
                "parts",
                "weight",
                "dim",
            )
        }),
        ("Descriptions", {
            "classes": ("collapse",),
            "fields": (
                "lego_description",
                "brickeconomy_description",
            )
        }),
    )

    def display_name(self, obj):
        return str(obj)

    display_name.short_description = "Set Name"



@admin.register(Images)
class ImagesAdmin(admin.ModelAdmin):
    list_display = (
        "set",
        "image_preview",
    )
    search_fields = ("set__set_id",)

    def image_preview(self, obj):
        return format_html(
            '<img src="{}" style="height:80px;" />',
            obj.link
        )

    image_preview.short_description = "Preview"

@admin.register(Sellers)
class SellersAdmin(admin.ModelAdmin):
    list_display = (
        "set",
        "source",
        "usd_price",
        "condition",
        "country",
        "quantity",
    )
    list_filter = ("source", "country", "condition")
    search_fields = ("set__set_id", "name")
    autocomplete_fields = ("set",)
    list_select_related = ("set",)
    list_per_page = 20