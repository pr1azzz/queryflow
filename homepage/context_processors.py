from categories.models import Category


def site_info(request):
    return {"site_name": "QueryFlow",
            "active_category_count": Category.objects.filter(
                is_active=True).count()}
