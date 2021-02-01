from django.contrib import admin

from care.transaction.models import Transaction, TransactionConsumer
from care.transaction.models import TransactionRecurring, TransactionRecurringConsumer
from care.transaction.models import TransactionReal
from care.transaction.models import Modification

class TransactionConsumerInline(admin.TabularInline):
    model = TransactionConsumer
    extra = 0

class TransactionAdmin(admin.ModelAdmin):
    fieldsets = [
        (None, {'fields': ['what']}),
        (None, {'fields': ['date']}),
        (None, {'fields': ['amount']}),
        (None, {'fields': ['group_account']}),
        (None, {'fields': ['buyer']}),
    ]
    list_display = ('what', 'amount', 'group_account', 'buyer', 'date')
    list_filter = ['date']
    search_fields = ['what']
    date_hierarchy = 'date'
    inlines = (TransactionConsumerInline, )

    def save_related(self, request, form, formset, change):
        super().save_related(request, form, formset, change)
        form.instance.update_total_weight()


admin.site.register(Transaction, TransactionAdmin)

class TransactionRecurringConsumerInline(admin.TabularInline):
    model = TransactionRecurringConsumer
    extra = 0

class TransactionRecurringAdmin(admin.ModelAdmin):
    fieldsets = [
        (None, {'fields': ['what']}),
        (None, {'fields': ['date']}),
        (None, {'fields': ['every']}),
        (None, {'fields': ['amount']}),
        (None, {'fields': ['group_account']}),
        (None, {'fields': ['buyer']}),
    ]
    list_display = ('what', 'amount', 'group_account', 'buyer', 'date', 'every')
    list_filter = ['date']
    search_fields = ['what']
    date_hierarchy = 'date'
    inlines = (TransactionRecurringConsumerInline, )

    def save_related(self, request, form, formset, change):
        super().save_related(request, form, formset, change)
        form.instance.update_total_weight()

admin.site.register(TransactionRecurring, TransactionRecurringAdmin)


class TransactionRealAdmin(admin.ModelAdmin):
    fieldsets = [
        (None, {'fields': ['amount']}),
        (None, {'fields': ['sender']}),
        (None, {'fields': ['receiver']}),
        (None, {'fields': ['comment']}),
        (None, {'fields': ['group_account']}), ]
    list_display = ('amount', 'sender', 'receiver', 'group_account', 'comment', 'date')
    list_filter = ['date']
    search_fields = ['what']
    date_hierarchy = 'date'

admin.site.register(TransactionReal, TransactionRealAdmin)


class ModificationAdmin(admin.ModelAdmin):
    fieldsets = [
        (None, {'fields': ['date']}),
        (None, {'fields': ['user']}), ]
    list_display = ('date', 'user')

admin.site.register(Modification, ModificationAdmin)
