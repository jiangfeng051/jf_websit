#date:2018/7/27
from dbutils.connectdb import DbConnect
from backend.sendmail import email
def analyze_log(rule,data_log,date_now):
    rule_condtion = rule['rule_condtion']
    rule_price= int(rule['rule_price'])
    urle_id = rule['rule_id']
    rule_name = rule['rule_name']
    rule_list = rule['rule_content'].split(',')
    ret_count = 0
    state = True
    for hit in data_log:
        for keyword in rule_list:
            if keyword not in hit['_source']['message']:
                state = False
                break
        if state:
            ret_count += 1
        else:
            state = True
    print(ret_count,rule_price,rule_condtion)
    if rule_condtion=='lt':
        if ret_count<rule_price:
            message='{date}触发了警告'.format(date=rule_name)
            email(message)
            warning_flag = 1
        else:
            warning_flag = 2
    if rule_condtion=='gt':
        if  ret_count>rule_price:
            message='{date}触发了警告'.format(date=rule_name)
            email(message)
            warning_flag = 1
        else:
            warning_flag = 2
    #把结果存入到报警明细表
    db_conn = DbConnect()
    cursor = db_conn.connect()
    sql = "insert into rule_log_detail (rule_id,result,warning,gmt_create) value (%s,%s,%s,%s)"
    cursor.execute(sql,[urle_id,ret_count,warning_flag,date_now,])
    db_conn.close()