from django.db import models


class RefBook(models.Model):
    code = models.CharField(max_length=100, unique=True)
    name = models.CharField(max_length=300)
    description = models.TextField(blank=True)

    class Meta:
        verbose_name = "Справочник"
        verbose_name_plural = "Справочники"
        constraints = [
            models.UniqueConstraint(fields=["code"], name="unique_refbook_code"),
        ]

    def __str__(self):
        return f"{self.code} - {self.name}"


class Version(models.Model):
    refbook = models.ForeignKey(RefBook, on_delete=models.CASCADE, related_name="versions")
    version = models.CharField(max_length=50)
    start_date = models.DateField()

    class Meta:
        verbose_name = "Версия справочника"
        verbose_name_plural = "Версии справочников"
        constraints = [
            models.UniqueConstraint(fields=["refbook", "version"], name="unique_version_per_refbook"),
            models.UniqueConstraint(fields=["refbook", "start_date"], name="unique_start_date_per_refbook"),
        ]

    def __str__(self):
        return f"{self.refbook.code} v{self.version}"


class Element(models.Model):
    version = models.ForeignKey(Version, on_delete=models.CASCADE, related_name="elements")
    code = models.CharField(max_length=100)
    value = models.CharField(max_length=300)

    class Meta:
        verbose_name = "Элемент справочника"
        verbose_name_plural = "Элементы справочников"
        constraints = [
            models.UniqueConstraint(fields=["version", "code"], name="unique_element_code_per_version"),
        ]

    def __str__(self):
        return f"{self.code} - {self.value}"
