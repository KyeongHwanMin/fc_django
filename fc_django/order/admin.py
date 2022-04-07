from django.contrib import admin
from django.utils.html import format_html  # 태그를 사용할 수 있게 해줌. 보통은 <b>test</b> 이렇게 출력됨
from .models import Order
from django.db.models import F, Q  # F 일괄적으로 값을 업데이트
from django.db import transaction

# 커스텀 행위에 대한 로그를 남기기 위해 두줄 추가
from django.contrib.admin.models import LogEntry, CHANGE
from django.contrib.contenttypes.models import ContentType


def refund(self, request, queryset):
    # 기본 방법
    # for obj in queryset:  # 목록에서 선택된 것(queryset)
    #     if obj.status == '환불': continue
    #     obj.product.stock += obj.quantity
    #     obj.product.save()
    # 쿼리셋 이용방법
    with transaction.atomic():  # 모든 동작을 하나의 단위로 실행. 트렌젝션
        qs = queryset.filter(~Q(status='환불'))  # 환불이 아닌것 (NOT)

        ct = ContentType.objects.get_for_model(queryset.model)  # 어떤 모델을 사용하는지 확인
        for obj in qs:
            obj.product.stock += obj.quantity
            obj.product.save()

            LogEntry.objects.log_action(  # static 함수임.
                user_id=request.user.id,
                content_type_id=ct.pk,
                object_id=obj.pk,
                object_repr='주문 환불',  # obj설명
                action_flag=CHANGE,  # 추가인지, 수정인지
                change_message='주문 환불'
            )
        qs.update(status='환불')


refund.short_description = '환불'  # refund 이름 지정


class OrderAdmin(admin.ModelAdmin):
    list_filter = ('status',)
    list_display = ('fcuser', 'product', 'styled_status', 'action')
    change_list_template = 'admin/order_change_list.html'
    change_form_template = 'admin/order_change_from.html'

    actions = [
        refund
    ]

    def action(self, obj):
        if obj.status != '환불':
            return format_html(
                f'<input type="button" value="환불" onclick="order_refund_submit({obj.id})" class="btn btn-primary btn-sm">')

    def styled_status(self, obj):  # obj == 각 레코드를 의미
        if obj.status == '환불':
            return format_html(f'<span style="color:red">{obj.status}</span>')
        if obj.status == '결제완료':
            return format_html(f'<span style="color:green">{obj.status}</span>')
        return format_html(f'<b>{obj.status}</b>')

    def changelist_view(self, request, extra_context=None):
        extra_context = {'title': '주문 목록'}

        if request.method == 'POST':
            obj_id = request.POST.get('obj_id')
            if obj_id:
                qs = Order.objects.filter(pk=obj_id)
                ct = ContentType.objects.get_for_model(qs.model)
                for obj in qs:
                    obj.product.stock += obj.quantity
                    obj.product.save()

                    LogEntry.objects.log_action(
                        user_id=request.user.id,
                        content_type_id=ct.pk,
                        object_id=obj.pk,
                        object_repr='주문 환불',
                        action_flag=CHANGE,
                        change_message='주문 환불'
                    )
                qs.update(status='환불')

        return super().changelist_view(request, extra_context)

    def changeform_view(self, request, object_id=None, form_url="", extra_context=None):
        order = Order.objects.get(pk=object_id)
        extra_context = {'title': f"'{order.fcuser.email}'의 '{order.product.name}' 주문 수정하기"}
        extra_context['show_save_and_add_another'] = False
        extra_context['show_save_and_continue'] = False
        return super().changeform_view(request, object_id, form_url, extra_context)

    styled_status.shor_description = '상태'


admin.site.register(Order, OrderAdmin)
