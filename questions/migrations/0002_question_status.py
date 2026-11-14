from django.db import migrations, models


def forwards(apps, schema_editor):
    Question = apps.get_model("questions", "Question")
    qs = Question.objects.using(schema_editor.connection.alias)
    qs.filter(is_closed=True).update(status="closed")
    qs.filter(is_closed=False).update(status="open")


def backwards(apps, schema_editor):
    Question = apps.get_model("questions", "Question")
    qs = Question.objects.using(schema_editor.connection.alias)
    qs.update(is_closed=False)
    qs.filter(status="closed").update(is_closed=True)


class Migration(migrations.Migration):
    dependencies = [("questions", "0001_initial")]
    operations = [
        migrations.AddField(
            model_name="question", name="status",
            field=models.CharField(
                "Статус", max_length=12, default="open",
                choices=[("open", "Открыт"), ("closed", "Закрыт"),
                         ("withdrawn", "Отозван")])),
        migrations.RunPython(forwards, backwards),
        migrations.RemoveField(model_name="question", name="is_closed"),
    ]
