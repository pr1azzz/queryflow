import categories.models
from django.db import migrations, models


def populate_slugs(apps, schema_editor):
    Category = apps.get_model("categories", "Category")
    for category in Category.objects.using(schema_editor.connection.alias).all():
        category.slug = f"category-{category.pk}"
        category.save(update_fields=["slug"])


class Migration(migrations.Migration):
    dependencies = [("categories", "0001_initial")]
    operations = [
        migrations.AddField(model_name="category", name="slug",
                            field=models.SlugField(null=True)),
        migrations.RunPython(populate_slugs, migrations.RunPython.noop),
        migrations.AlterField(
            model_name="category", name="slug", field=models.SlugField(
                "Адрес", unique=True, default=categories.models.category_slug)),
    ]
