from django import forms
from .models import Order
from product.models import Product
from fcuser.models import Fcuser
from django.db import transaction




class RegisterForm(forms.Form):
    # product/view orderform에서 request 받기
    def __init__(self, request, *args, **kwargs):# 세션정보 받기 위함
        super().__init__(*args, **kwargs)
        self.request = request


    quantity = forms.IntegerField(
        error_messages={
            'required': '수량을 입력해주세요.'
        }, label='상품명'
    )
    rpoduct = forms.IntegerField(
        error_messages={
            'required': '상품설명을 입력해주세요.'
        }, label='상품설명', widget=forms.HiddenInput
    )

    def clean(self):
        cleaned_data = super().clean()
        quantity = cleaned_data.get('quantity')
        product = cleaned_data.get('product')
        print(self.request.session)
        fcuser = self.request.session.get('user')

        if quantity and product and fcuser:
            with transaction.atomic(): # with : transaction 처리
                prod = Product.objects.get(pk=product)
                order = Order(
                    quantity=quantity,
                    product=Product.objects.get(pk=product),
                    fcuer=Fcuser.objetcts.get(email=fcuser)
                )
                order.save()
                prod.stock -= quantity
                prod.save()

        else:
            self.product = product
            self.add_error('quantity', '값이 없습니다.')
            self.add_error('product', '값이 없습니다.')


