from django import forms
from django.core.exceptions import ValidationError
from django.db import transaction
from django.db import models


class SelectShareConsumersWidget(forms.CheckboxSelectMultiple):
    option_template_name = "transaction/consumers_select_row.html"
    default_weight = 1.0

    def optgroups(self, name, value, attrs=None):
        groups = []
        has_selected = False

        for index, (option_value, option_label) in enumerate(self.choices):
            if option_value is None:
                option_value = ""

            subgroup = []
            if isinstance(option_label, (list, tuple)):
                group_name = option_value
                subindex = 0
                choices = option_label
            else:
                group_name = None
                subindex = None
                choices = [(option_value, option_label)]
            groups.append((group_name, subgroup, index))

            for subvalue, sublabel in choices:
                weight = None
                if not has_selected or self.allow_multiple_selected:
                    weight = value.get(subvalue, None)
                has_selected |= weight is not None
                subgroup.append(
                    self.create_option(
                        name,
                        subvalue,
                        sublabel,
                        weight is not None,
                        index,
                        subindex=subindex,
                        attrs=attrs,
                        weight=weight,
                    )
                )
                if subindex is not None:
                    subindex += 1
        return groups

    @staticmethod
    def _weight_name(name, value):
        return "{name}_weight_{id}".format(name=name, id=value)

    def create_option(self, *args, weight=None, **kwargs):
        option = super().create_option(*args, **kwargs)
        weight_options = {
            "attrs": {
                "class": "",
                "title": "",
                "id": option["attrs"]["id"] + "_weight",
            },
            "value": weight or self.default_weight,
            "label": "share proportion",
            "name": self._weight_name(option["name"], option["value"]),
        }
        option["weight"] = weight_options
        return option

    def get_context(self, *args, **kwargs):
        ctx = super().get_context(*args, **kwargs)
        return ctx

    def format_value(self, value):
        if value is None:
            return {}
        assert isinstance(value, dict)
        return value

    def value_from_datadict(self, data, files, name):
        selected = super().value_from_datadict(data, files, name)
        out = {}
        for value in selected:
            out[value] = data.get(self._weight_name(name, value), self.default_weight)
        return out


class ShareConsumersField(forms.ModelMultipleChoiceField):
    widget = SelectShareConsumersWidget

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def prepare_value(self, value):
        if isinstance(value, dict):
            prepare_value = super().prepare_value
            out = {int(prepare_value(k)): v for k, v in value.items()}
            return out
        return super().prepare_value(value)

    def clean(self, value):
        value = self.prepare_value(value)
        if self.required and not value:
            raise ValidationError(self.error_messages["required"], code="required")
        elif not self.required and not value:
            return self.queryset.none()
        if not isinstance(value, dict):
            raise ValidationError(self.error_messages["list"], code="list")
        qs = self._check_values(value.keys())
        out = {
            "qs": qs,
            "weights": value,
        }
        self.run_validators(value)
        return out


class WeightedManyToManyField(models.ManyToManyField):
    def __init__(self, *args, weight_field, through, **kwargs):
        super().__init__(*args, through=through, **kwargs)
        self.weight_field = weight_field

    def deconstruct(self):
        name, path, args, kwargs = super().deconstruct()
        kwargs["weight_field"] = self.weight_field
        return (name, path, args, kwargs)

    def save_form_data(self, instance, data):
        if isinstance(data, dict):
            related_manager = getattr(instance, self.attname)
            qs = data["qs"]
            weights = data["weights"]

            through_model = related_manager.through
            through_to_source = self.m2m_field_name()
            through_to_dest = self.m2m_reverse_field_name()

            with transaction.atomic():
                related_manager.clear()
                for dest_obj in qs:
                    values = {
                        through_to_source: instance,
                        through_to_dest: dest_obj,
                        self.weight_field: weights[dest_obj.pk],
                    }
                    through_model.objects.create(**values)
        else:
            super().save_form_data(instance, data)

    def value_from_object(self, obj):
        related_manager = getattr(obj, self.attname)
        through_to_source = self.m2m_field_name()
        through_to_dest = self.m2m_reverse_field_name()
        through_model = related_manager.through

        links = through_model.objects.filter(**{through_to_source: obj.pk})
        return {
            getattr(link, through_to_dest).pk: getattr(link, self.weight_field)
            for link in links.all()
        }
