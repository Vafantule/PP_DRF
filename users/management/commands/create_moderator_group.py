from typing import List

from django.contrib.auth.models import Group, Permission
from django.core.management.base import BaseCommand

from materials.models import Course, Lesson


class Command(BaseCommand):
    """
    Команда для создания группы "moderators"  с заданными правами.
    """
    def _get_permission(self, codename: str) -> Permission:
        try:
            return Permission.objects.get(codename=codename)
        except Permission.DoesNotExist:
            raise RuntimeError(f"Разрешение по операции '{codename}' не найдено.")

    def handle(self, *args, **options) -> None:
        group, created = Group.objects.get_or_create(name="moderators")
        if created:
            self.stdout.write(self.style.SUCCESS("Группа 'moderators' создана."))
        else:
            self.stdout.write(self.style.WARNING("Группа 'moderators' уже существует."))

        desired_operations = [
            f"view_{Course._meta.model_name}",
            f"change_{Course._meta.model_name}",
            f"view_{Lesson._meta.model_name}",
            f"change_{Lesson._meta.model_name}"
        ]

        permissions_to_add: List[Permission] = []
        missing: List[str] = []
        for operation in desired_operations:
            try:
                permission = self._get_permission(operation)
                permissions_to_add.append(permission)
            except RuntimeError:
                missing.append(operation)

        if missing:
            self.stdout.write(self.style.ERROR("Не все разрешения найдены. "
                                               f"Отсутствуют операции: {', '.join(missing)}"))
        group.permissions.clear()
        group.permissions.add(*permissions_to_add)

        self.stdout.write(self.style.SUCCESS(f"Группе 'moderators' назначены права: "
                                             f"{', '.join([permission.codename for permission in permissions_to_add])}"
                                             ))
        self.stdout.write(self.style.SUCCESS("Назначьте пользователей в группу 'moderators'."))
