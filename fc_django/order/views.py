from django.shortcuts import render, redirect
from django.views.generic import FormView

from .forms import RegisterForm


class OrderCreate(FormView):
    form_class = RegisterForm
    success_url = '/product/'

    def form_invalid(self, form): # 실패했을 경우
       return redirect('/product/' + str(form.product))

    # formview 안에서도 reqeust를 전달 해야함.
    def get_form_kwargs(self, **kwargs):  # from을 생성할 때 인자값을 전달
        kw = super().get_form_kwargs(**kwargs)
        kw.update({ # form을 생성할 때 request 인자 값도 같이 전달.
            'request': self.request
        })
        return kw
