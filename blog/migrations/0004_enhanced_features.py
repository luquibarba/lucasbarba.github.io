# Generated manually for enhanced features
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('blog', '0003_alter_category_options'),
    ]

    operations = [
        # Agregar campos al modelo Post
        migrations.AddField(
            model_name='post',
            name='likes',
            field=models.PositiveIntegerField(default=0),
        ),
        migrations.AddField(
            model_name='post',
            name='dislikes',
            field=models.PositiveIntegerField(default=0),
        ),
        migrations.AddField(
            model_name='post',
            name='views',
            field=models.PositiveIntegerField(default=0),
        ),
        migrations.AddField(
            model_name='post',
            name='featured',
            field=models.BooleanField(default=False, help_text='Post destacado en portada'),
        ),
        
        # Agregar campos al modelo Category
        migrations.AddField(
            model_name='category',
            name='icon',
            field=models.CharField(default='fas fa-tag', help_text='Ícono de FontAwesome', max_length=50),
        ),
        migrations.AddField(
            model_name='category',
            name='color',
            field=models.CharField(default='#3b2342', help_text='Color hexadecimal', max_length=7),
        ),
        
        # Modificar campos del modelo Comment
        migrations.AlterField(
            model_name='comment',
            name='body',
            field=models.TextField(help_text='Máximo 1000 caracteres', max_length=1000),
        ),
        migrations.AddField(
            model_name='comment',
            name='is_featured',
            field=models.BooleanField(default=False, help_text='Comentario destacado'),
        ),
        migrations.AddField(
            model_name='comment',
            name='email',
            field=models.EmailField(blank=True, help_text='Email opcional para respuestas', max_length=254),
        ),
        migrations.AddField(
            model_name='comment',
            name='ip_address',
            field=models.GenericIPAddressField(blank=True, null=True),
        ),
        
        # Crear modelo PostLike
        migrations.CreateModel(
            name='PostLike',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('ip_address', models.GenericIPAddressField()),
                ('is_like', models.BooleanField()),
                ('created_on', models.DateTimeField(auto_now_add=True)),
                ('post', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='blog.post')),
            ],
            options={
                'unique_together': {('post', 'ip_address')},
            },
        ),
        
        # Modificar ordenamiento de Comment
        migrations.AlterModelOptions(
            name='comment',
            options={'ordering': ['-is_featured', '-created_on']},
        ),
        migrations.AlterModelOptions(
            name='post',
            options={'ordering': ['-created_on']},
        ),
    ]