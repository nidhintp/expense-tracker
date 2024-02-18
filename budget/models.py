from django.db import models
from django.contrib.auth.models import User
class Transactions(models.Model):
    title=models.CharField(max_length=200)
    amount=models.PositiveIntegerField()
    options=(
        ("expense","expense"),
        ("income","income")
    )
    type=models.CharField(max_length=200,choices=options,default="expense")
    cat_options=(
        ("fuel","fuel"),
        ("food","food"),
        ("entertainment","entertainment"),
        ("bills","bills"),
        ("emi","emi"),
        ("miscellaneous","miscellaneous")
    )
    category=models.CharField(max_length=200,choices=cat_options,default="miscellaneous")
    created_date=models.DateTimeField(auto_now_add=True,blank=True)
    user_object=models.ForeignKey(User,on_delete=models.CASCADE)

    def __str__(self):
        return self.title
