from django.contrib import admin
from django.utils.html import format_html # 태그를 사용할 수 있게 해줌. 보통은 <b>test</b> 이렇게 출력됨
from .models import Order



class OrderAdmin(admin.ModelAdmin):
    list_filter = ('status',)
    list_display = ('fcuser', 'product', 'styled_status')

    def styled_status(self, obj): # obj == 각 레코드를 의미
        if obj.status == '환불':
            return format_html(f'<span style="color:red">{obj.status}</span>')
        if obj.status == '결제완료':
            return format_html(f'<span style="color:green">{obj.status}</span>')
        return format_html(f'<b>{obj.status}</b>')
    
    def changelist_view(self, request, extra_context=None):
        extra_context = {'title': '주문 목록'}
        return super().changelist_view(request, extra_context)

    def changeform_view(self, request, object_id=None, form_url="", extra_context=None):
        order = Order.objects.get(pk=object_id)
        extra_context = {'title': f"'{order.fcuser.email}'의 '{order.product.name}' 주문 수정하기"}
        return super().changeform_view(request, object_id, form_url, extra_context)

    styled_status.shor_description = '상태'

admin.site.register(Order, OrderAdmin)
