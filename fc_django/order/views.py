from django.shortcuts import render, redirect
from django.views.generic import FormView, ListView
from .models import Order
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

class OrderList(ListView):
    template_name = 'order.html'
    context_object_name = 'order_list'

    #필드에서 queryset을 쓰려면 session이 필요하기 때문에 함수 이용.
    def get_queryset(self, **kwargs):
        queryset = Order.objects.filter(fcuser__email=self.request.session.get('user'))
        return queryset
