from django.shortcuts import render
from django.shortcuts import redirect
from . import models
from . import forms


import hashlib

# Create your views here.


def index(request):
    if not request.session.get('is_login', None):
        return redirect('/login/')
    return render(request, 'login/index.html')


def login(request):
    if request.session.get('is_login', None):  # 不允许重复登陆
        return redirect('/index/')
    if request.method == 'POST':
        login_form = forms.UserForm(request.POST)
        message = '请检查填写的内容.'
        if login_form.is_valid():
            username = login_form.cleaned_data.get('username')
            password = login_form.cleaned_data.get('password')

            try:
                user = models.User.objects.get(name=username)
            except :
                message = '用户不存在.'
                return render(request, 'login/login.html', locals())

            if not user.has_confirmed:
                message = '该用户还未经过邮件确认.'
                return render(request, 'login/login.html', locals())

            if user.password == hash_code(password):
                """
                通过下面的语句，我们往session字典内写入用户状态和数据：
                你完全可以往里面写任何数据，不仅仅限于用户相关！
                既然有了session记录用户登录状态，那么就可以完善我们的登出视图函数了：
                """
                request.session['is_login'] = True
                request.session['user_id'] = user.id
                request.session['user_name'] = user.name
                return redirect('/index/')
            else:
                message = '密码不正确.'
                return render(request, 'login/login.html', locals())
        else:
            return render(request, 'login/login.html', locals())

    login_form = forms.UserForm()
    return render(request, 'login/login.html', locals())


"""
这里增加了message变量，用于保存提示信息。当有错误信息的时候，
将错误信息打包成一个字典，然后作为第三个参数提供给render方法。
这个数据字典在渲染模板的时候会传递到模板里供你调用。
为了在前端页面显示信息，还需要对login.html进行修改：
"""


import datetime


def make_confirm_string(user):
    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    code = hash_code(user.name, now)
    models.ConfirmString.objects.create(code=code, user=user)
    return code


"""
make_confirm_string()方法接收一个用户对象作为参数。
首先利用datetime模块生成一个当前时间的字符串now，
再调用我们前面编写的hash_code()方法以用户名为基础，
now为‘盐’，生成一个独一无二的哈希值，再调用ConfirmString模型的create()方法，
生成并保存一个确认码对象。最后返回这个哈希值。

send_email(email, code)方法接收两个参数，
分别是注册的邮箱和前面生成的哈希值，代码如下：
"""

from django.conf import settings


def send_email(email, code):

    from django.core.mail import EmailMultiAlternatives

    subject = '来自www.twinkle.com的注册确认邮件'

    text_content = '''感谢注册Twinkle的账号,这里是宇豪同学的blog. \
                    如果你看到这条消息,说明你的邮箱不支持提供HTML链接功能,请联系管理员.'''

    html_content = '''
            <p>感谢注册< a href="http://{}/confirm/?code={}" target=blank>www.twinkle.com</a>, \
            这里是宇豪同学的blog.</p>
            <p>请点击链接完成注册确认.</p>
            <p>此链接有效期为{}天.</p>
            '''.format('127.0.0.1:8000', code, settings.CONFIRM_DAYS)
    msg = EmailMultiAlternatives(subject, text_content, settings.EMAIL_HOST_USER, [email])
    msg.attach_alternative(html_content, "text/html")
    msg.send()


"""
首先我们需要导入settings配置文件from django.conf import settings。

邮件内容中的所有字符串都可以根据你的实际情况进行修改。
其中关键在于<a href=''>中链接地址的格式，
我这里使用了硬编码的'127.0.0.1:8000'，请酌情修改，
url里的参数名为code，它保存了关键的注册确认码，
最后的有效期天数为设置在settings中的CONFIRM_DAYS。
所有的这些都是可以定制的！
"""


def register(request):
    if request.session.get('is_login', None):
        return redirect('/index/')

    if request.method == 'POST':
        register_form = forms.RegisterForm(request.POST)
        message = "请检查填写的内容！"
        if register_form.is_valid():
            username = register_form.cleaned_data.get('username')
            password1 = register_form.cleaned_data.get('password1')
            password2 = register_form.cleaned_data.get('password2')
            email = register_form.cleaned_data.get('email')
            sex = register_form.cleaned_data.get('sex')

            if password1 != password2:
                message = '两次输入的密码不同！'
                return render(request, 'login/register.html', locals())
            else:
                same_name_user = models.User.objects.filter(name=username)
                if same_name_user:
                    message = '用户名已经存在'
                    return render(request, 'login/register.html', locals())
                same_email_user = models.User.objects.filter(email=email)
                if same_email_user:
                    message = '该邮箱已经被注册了！'
                    return render(request, 'login/register.html', locals())

                new_user = models.User()
                new_user.name = username
                new_user.password = hash_code(password1)
                new_user.email = email
                new_user.sex = sex
                new_user.save()

                code = make_confirm_string(new_user)
                send_email(email, code)

                message = '请前往邮箱进行确认！'
                return render(request, 'login/confirm.html', locals())
        else:
            return render(request, 'login/register.html', locals())
    register_form = forms.RegisterForm()
    return render(request, 'login/register.html', locals())


"""
从大体逻辑上，也是先实例化一个RegisterForm的对象，然后使用is_valide()验证数据，
再从cleaned_data中获取数据。
重点在于注册逻辑，首先两次输入的密码必须相同，其次不能存在相同用户名和邮箱，
最后如果条件都满足，利用ORM的API，创建一个用户实例，然后保存到数据库内。
对于注册的逻辑，不同的生产环境有不同的要求，请跟进实际情况自行完善，
这里只是一个基本的注册过程，不能生搬照抄。
"""


def logout(request):
    if not request.session.get('is_login', None):
        # 如果本来就未登录,也就没登出这一步骤
        return redirect('/login/')

    request.session.flush()
    """
    flush()方法是比较安全的一种做法，而且一次性将session中的所有内容全部清空，
    确保不留后患。但也有不好的地方，那就是如果你在session中夹带了一点‘私货’，
    会被一并删除，这一点一定要注意。
    """
    # 或者使用下面的方法
    # del request.session['is_login']
    # del request.session['user_id']
    # del request.session['user_name']
    return redirect('/login/')


import hashlib


def hash_code(s, salt='mysite'):  # 加点盐
    h = hashlib.sha256()
    s += salt
    h.update(s.encode())  # update方法只接收bytes类型
    return h.hexdigest()


"""
使用了sha256算法，加了点盐。具体的内容可以参考站点内的Python教程中hashlib库章节。

然后，我们还要对login()和register()视图进行一下修改：
"""


"""
01
每个视图函数都至少接收一个参数，并且是第一位置参数，该参数封装了当前请求的所有数据；
通常将第一参数命名为request，当然也可以是别的；
request.method中封装了数据请求的方法，如果是“POST”（全大写），
将执行if语句的内容，如果不是，直接返回最后的render()结果，也就是正常的登录页面；
request.POST封装了所有POST请求中的数据，这是一个字典类型，可以通过get方法获取具体的值。
类似get('username')中的键‘username’是HTML模板中表单的input元素里‘name’属性定义的值。
所以在编写form表单的时候一定不能忘记添加name属性。
利用print函数在开发环境中验证数据；
利用redirect方法，将页面重定向到index页
get方法是Python字典类型的内置方法，它能够保证在没有指定键的情况下，
返回一个None，从而确保当数据请求中没有username或password键时不会抛出异常；
通过if username and password:确保用户名和密码都不为空；
通过strip方法，将用户名前后无效的空格剪除；
更多的数据验证需要根据实际情况增加，原则是以最低的信任度对待发送过来的数据。

02
在顶部额外导入了redirect，用于logout后，页面重定向到‘/login/’这个url，
当然你也可以重定向到别的页面；另外三个视图都返回一个render调用，
render方法接收request作为第一个参数，要渲染的页面为第二个参数，
以及需要传递给页面的数据字典作为第三个参数（可以为空），表示根据请求的部分，
以渲染的HTML页面为主体，使用模板语言将数据字典填入，然后返回给用户的浏览器。
渲染的对象为login目录下的html文件，这是一种安全可靠的文件组织方式，
我们现在还没有创建这些文件。

03
首先要在顶部导入models模块；
使用try异常机制，防止数据库查询失败的异常；
如果未匹配到用户，则执行except中的语句；注意这里没有区分异常的类型，
因为在数据库访问过程中，可能发生很多种类型的异常，我们要对用户屏蔽这些信息，
不可以暴露给用户，而是统一返回一个错误提示，比如用户名不存在。这是大多数情况下的通用做法。
当然，如果你非要细分，也不是不行。
models.User.objects.get(name=username)是Django提供的最常用的数据查询API，
具体含义和用法可以阅读前面的章节，不再赘述；
通过user.password == password进行密码比对，成功则跳转到index页面，失败则返回登录页面。
重启服务器，然后在登录表单内，使用错误的用户名和密码，
以及我们先前在admin中创建的合法的测试用户，分别登录，看看效果。

04
在顶部要导入我们写的forms模块:from . import forms
对于非POST方法发送数据时，比如GET方法请求页面，返回空的表单，让用户可以填入数据；
对于POST方法，接收表单数据，并验证；
使用表单类自带的is_valid()方法一步完成数据验证工作；
验证成功后可以从表单对象的cleaned_data数据字典中获取表单的具体值；
如果验证不通过，则返回一个包含先前数据的表单给前端页面，方便用户修改。
也就是说，它会帮你保留先前填写的数据内容，而不是返回一个空表！
另外，这里使用了一个小技巧，Python内置了一个locals()函数，
它返回当前所有的本地变量字典，我们可以偷懒的将这作为render函数的数据字典参数值，
就不用费劲去构造一个形如{'message':message, 'login_form':login_form}的字典了。
这样做的好处当然是大大方便了我们，但是同时也可能往模板传入了一些多余的变量数据，
造成数据冗余降低效率。
"""


def user_confirm(request):
    code = request.GET.get('code', None)
    message = ''
    try:
        confirm = models.ConfirmString.objects.get(code=code)
    except:
        message = '无效的确认请求.'
        return render(request, 'login/confirm.html', locals())

    c_time = confirm.c_time
    now = datetime.datetime.now()
    if now > c_time + datetime.timedelta(settings.CONFIRM_DAYS):
        confirm.user.delete()
        message = '您的邮件已经过期,请重新注册.'
        return render(request, 'login/confirm.html', locals())
    else:
        confirm.user.has_confirmed = True
        confirm.user.save()
        confirm.delete()
        message = '感谢确认,请使用注册的账号登录.'
        return render(request, 'login/confirm.html', locals())


"""
通过request.GET.get('code', None)从请求的url地址中获取确认码;
先去数据库内查询是否有对应的确认码;
如果没有，返回confirm.html页面，并提示;
如果有，获取注册的时间c_time，加上设置的过期天数，这里是7天，然后与现在时间点进行对比；
如果时间已经超期，删除注册的用户，同时注册码也会一并删除，然后返回confirm.html页面，并提示;
如果未超期，修改用户的has_confirmed字段为True，并保存，表示通过确认了。然后删除注册码，
但不删除用户本身。最后返回confirm.html页面，并提示。
"""
