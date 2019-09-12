from flask import Blueprint

main = Blueprint('main', __name__)  # param: 蓝本名称， 蓝本所在的包

from . import views, errors  # 这行必须放在末尾 是为了避免循环应用
