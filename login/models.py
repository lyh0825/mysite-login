from django.db import models

# Create your models here.


class User(models.Model):

    gender = (
        ('male', "男"),
        ('female', "女"),
    )

    name = models.CharField(max_length=128, unique=True)
    password = models.CharField(max_length=256)
    email = models.EmailField(unique=True)
    sex = models.CharField(max_length=32, choices=gender, default="男")
    c_time = models.DateTimeField(auto_now_add=True)
    has_confirmed = models.BooleanField(default=False)
    """
    name: 必填，最长不超过128个字符，并且唯一，也就是不能有相同姓名；
    password: 必填，最长不超过256个字符（实际可能不需要这么长）；
    email: 使用Django内置的邮箱类型，并且唯一；
    sex: 性别，使用了一个choice，只能选择男或者女，默认为男；
    使用__str__方法帮助人性化显示对象信息；
    元数据里定义用户按创建时间的反序排列，也就是最近的最先显示；
    """
    # 注意：这里的用户名指的是网络上注册的用户名，不要等同于现实中的真实姓名，
    # 所以采用了唯一机制。如果是现实中的人名，那是可以重复的，
    # 肯定是不能设置unique的。另外关于密码，建议至少128位长度，原因后面解释。

    def __str__(self):
        return self.name

    class Meta:
        ordering = ["-c_time"]
        verbose_name = "用户"
        verbose_name_plural = "用户"


"""
既然要区分通过和未通过邮件确认的用户，那么必须给用户添加一个是否进行过邮件确认的属性。
另外，我们要创建一张新表，用于保存用户的确认码以及注册提交的时间。
"""


class ConfirmString(models.Model):
    code = models.CharField(max_length=256)
    user = models.OneToOneField('User', on_delete=models.CASCADE)
    c_time = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.user.name + ":  " + self.code

    class Meta:

        ordering = ["-c_time"]
        verbose_name = "确认码"
        verbose_name_plural = "确认码"


"""
User模型新增了has_confirmed字段，这是个布尔值，默认为False，也就是未进行邮件注册；
ConfirmString模型保存了用户和注册码之间的关系，一对一的形式；
code字段是哈希后的注册码；
user是关联的一对一用户；
c_time是注册的提交时间。
这里有个问题可以讨论一下：是否需要创建ConfirmString新表？可否都放在User表里？
我认为如果全都放在User中，不利于管理，查询速度慢，创建新表有利于区分已确认和未确认的用户。
最终的选择可以根据你的实际情况具体分析。

模型修改和创建完毕，需要执行migrate命令，一定不要忘了。

顺便修改一下admin.py文件，方便我们在后台修改和观察数据。
"""
