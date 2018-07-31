#date:2018/7/27


#mysql数据库配置
PY_MYSQL_CONN_DICT = {
    "host": '10.0.1.40',
    "port": 3306,
    "user": 'root',
    "passwd": 'zentech#123',
    "db": 'myeye',
    "charset": 'utf8'
}


#elasticsearch地址配置
elasticsearch_DICT = {
    'host':'10.0.1.70',
    'port':9200,
}

#邮箱配置
#发送邮箱地址
sendmailuser='quote@zentech-inc.com'
#发送邮箱的密码
sendmailpasswd='zentech#123'
#发送邮箱服务地址
smtpmail = 'smtp.zentech-inc.com'
#接收邮箱地址，多个地址用，分开
acceptmailuser=['jiangfeng@zentech-inc.com',]
#邮件名称
mailSubject = '错误报警'

