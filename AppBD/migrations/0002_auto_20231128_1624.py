# Generated by Django 3.2 on 2023-11-28 22:24

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('AppBD', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Cargo',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nombre', models.CharField(max_length=25)),
                ('descripcion', models.CharField(max_length=50)),
                ('salario', models.CharField(max_length=50)),
            ],
        ),
        migrations.CreateModel(
            name='Clientes',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nombre', models.CharField(max_length=25)),
                ('apellido', models.CharField(blank=True, max_length=25, null=True)),
                ('direccion', models.CharField(blank=True, max_length=50, null=True)),
                ('cedula', models.CharField(blank=True, max_length=25, null=True)),
                ('telefono', models.CharField(blank=True, max_length=10, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='Factura',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('fecha', models.DateField()),
                ('num_factura', models.IntegerField()),
                ('id_clientes', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='AppBD.clientes')),
                ('id_empleado', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='AppBD.empleado')),
            ],
        ),
        migrations.CreateModel(
            name='Item',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('descripcion', models.CharField(max_length=50)),
            ],
        ),
        migrations.CreateModel(
            name='NombreItem',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nombre', models.CharField(max_length=30)),
            ],
        ),
        migrations.CreateModel(
            name='Orden',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('descripcion', models.CharField(max_length=50)),
            ],
        ),
        migrations.CreateModel(
            name='TipoAlquiler',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nombre', models.CharField(max_length=30)),
                ('tarifa', models.FloatField()),
            ],
        ),
        migrations.CreateModel(
            name='ItemOrden',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('cantidad', models.IntegerField()),
                ('id_item', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='AppBD.item')),
                ('id_orden', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='AppBD.orden')),
            ],
        ),
        migrations.AddField(
            model_name='item',
            name='id_nombreItem',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='AppBD.nombreitem'),
        ),
        migrations.CreateModel(
            name='FacturaEmpleado',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('id_empleado', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='AppBD.empleado')),
                ('id_factura', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='AppBD.factura')),
            ],
        ),
        migrations.CreateModel(
            name='DetalleOrden',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('cantidad_items', models.IntegerField()),
                ('total', models.FloatField(blank=True, null=True)),
                ('id_orden', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='AppBD.orden')),
            ],
        ),
        migrations.CreateModel(
            name='DetalleAlquiler',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('cantidad_tiempo', models.CharField(max_length=30)),
                ('total', models.FloatField()),
                ('id_factura', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='AppBD.factura')),
            ],
        ),
        migrations.CreateModel(
            name='ClienteOrden',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('id_clientes', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='AppBD.clientes')),
                ('id_orden', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='AppBD.orden')),
            ],
        ),
        migrations.CreateModel(
            name='ClienteEmpleado',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('id_clientes', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='AppBD.clientes')),
                ('id_empleado', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='AppBD.empleado')),
            ],
        ),
        migrations.CreateModel(
            name='Alquiler',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('tiempo', models.CharField(max_length=50)),
                ('id_clientes', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='AppBD.clientes')),
                ('id_tipoAlquiler', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='AppBD.tipoalquiler')),
            ],
        ),
    ]
