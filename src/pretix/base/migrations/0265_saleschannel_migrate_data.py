# Generated by Django 4.2.8 on 2024-03-24 17:55

from django.db import migrations
from i18nfield.strings import LazyI18nString

from pretix.base.channels import get_all_sales_channel_types


def create_sales_channels(apps, schema_editor):
    channel_types = get_all_sales_channel_types()
    type_to_channel = dict()
    full_discount_set = set()

    Organizer = apps.get_model("pretixbase", "Organizer")
    for o in Organizer.objects.all():
        for t in channel_types.values():
            if not t.default_created:
                continue
            type_to_channel[t.identifier, o.pk] = o.sales_channels.get_or_create(
                type=t.identifier,
                defaults=dict(
                    identifier=t.identifier,
                    label=LazyI18nString.from_gettext(t.verbose_name),
                ),
            )[0]
            if t.discounts_supported:
                full_discount_set.add(t.identifier)
    full_set = set(type_to_channel.keys())

    Event = apps.get_model("pretixbase", "Event")
    for d in Event.objects.all():
        if set(d.sales_channels) != full_set:
            d.all_sales_channels = False
            d.save()
            for s in d.sales_channels:
                d.limit_sales_channels.add(type_to_channel[s, d.organizer_id])

    Item = apps.get_model("pretixbase", "Item")
    for d in Item.objects.select_related("event"):
        if set(d.sales_channels) != full_set:
            d.all_sales_channels = False
            d.save()
            for s in d.sales_channels:
                d.limit_sales_channels.add(type_to_channel[s, d.event.organizer_id])

    ItemVariation = apps.get_model("pretixbase", "ItemVariation")
    for d in ItemVariation.objects.select_related("item__event"):
        if set(d.sales_channels) != full_set:
            d.all_sales_channels = False
            d.save()
            for s in d.sales_channels:
                d.limit_sales_channels.add(type_to_channel[s, d.item.event.organizer_id])

    Discount = apps.get_model("pretixbase", "Discount")
    for d in Discount.objects.select_related("event"):
        if set(d.sales_channels) != full_discount_set:
            d.all_sales_channels = False
            d.save()
            for s in d.sales_channels:
                d.limit_sales_channels.add(type_to_channel[s, d.event.organizer_id])

    CheckinList = apps.get_model("pretixbase", "CheckinList")
    for c in CheckinList.objects.select_related("event"):
        for s in c.auto_checkin_sales_channel_types:
            c.auto_checkin_sales_channels.add(type_to_channel[s, d.event.organizer_id])

    Order = apps.get_model("pretixbase", "Order")
    for k, v in type_to_channel.items():
        Order.objects.filter(sales_channel_type=k, sales_channel__isnull=True).update(sales_channel=v)


class Migration(migrations.Migration):

    dependencies = [
        ("pretixbase", "0264_saleschannel_and_more"),
    ]

    operations = [
        migrations.RunPython(create_sales_channels, migrations.RunPython.noop),
    ]
