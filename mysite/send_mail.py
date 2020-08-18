"""
import os
from django.core.mail import send_mail


os.environ['DJANGO_SETTINGS_MODULE'] = 'mysite.settings'


# 一.在django中发送邮件
if __name__ == '__main__':

    send_mail(
        '来自www.yuhaoblog.com的测试邮件.',    # 第一个参数是邮件主题subject；
        '欢迎访问http:/127.0.0.1:8000/login,这里是宇豪同学的blog.', # 第二个参数是邮件具体内容；
        'yuhaotongxue0825@sina.com',    # 第三个参数是邮件发送方，需要和你settings中的一致；
        ['1982164667@qq.com'],  # 第四个参数是接受方的邮件地址列表。

    )
"""
# 二.发送HTML格式的邮件
import os
from django.core.mail import EmailMultiAlternatives


os.environ['DJANGO_SETTINGS_MODULE'] = 'mysite.settings'


if __name__ == "__main__":


    subject, from_email, to = '来自twinkle的测试邮件.', 'yuhaotongxue0825@sina.com', '1982164667@qq.com'
    text_content = '欢迎访问www.liuyuhao0825.com,这是宇豪同学的blog.什么时候显示这个???'
    html_content = '<p>欢迎访问<a href="http://www.4399.com" target=blank>www.liuyuhao0825.com</a>,这是宇豪同学的blog.</p>'

    # '<p>欢迎访问<a href="实际点击访问网址" target=blank>邮件发送时展示网址</a>,这是宇豪同学的blog.</p>'

    msg = EmailMultiAlternatives(subject, text_content, from_email, [to])
    msg.attach_alternative(html_content, "text/html")
    msg.send()

    # 其中的text_content是用于当HTML内容无效时的替代txt文本。