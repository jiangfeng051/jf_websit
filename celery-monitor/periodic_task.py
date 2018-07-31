#date:2018/7/27
#date:2018/7/25
import os
BASEDIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
from celery import Celery
from celery.schedules import crontab
from elasticsearch import Elasticsearch
import datetime
from conf import settings
from backend.analyze_log import analyze_log
from dbutils.connectdb import DbConnect
from concurrent.futures import ProcessPoolExecutor
from concurrent.futures import ThreadPoolExecutor
import datetime

app = Celery(
         'task',
          broker = 'redis://:jiangfeng@10.0.1.71:7000',
          backend='redis://:jiangfeng@10.0.1.71:7000',
)


@app.on_after_configure.connect
def setup_periodic_tasks(sender, **kwargs):
    # Calls test('hello') every 10 seconds.
    # sender.add_periodic_task(10.0, test.s('hello'), name='add every 10')

    # Calls test('world') every 30 seconds
    # sender.add_periodic_task(30.0, test.s('world'), )

    # Executes every Monday morning at 7:30 a.m.
    sender.add_periodic_task(
        crontab(minute='*/5',),
        monitor.s(5)
    )


@app.task
def test(arg):
    print(arg)

@app.task
def monitor(time):
    es = Elasticsearch([{'host': settings.elasticsearch_DICT['host'], 'port': settings.elasticsearch_DICT['port']}])
    torday = datetime.datetime.now().strftime("%Y.%m.%d")
    yesterday = (datetime.datetime.now() + datetime.timedelta(days=-1)).strftime("%Y.%m.%d")
    #检测Elasticsearch索引，如不存在则创建索引，由于elk使用的是是UTC时间，有8小时的时差，所以必须把今天和昨天的索引都加上，不然0点到8点的数据会获取不到
    es_index = 'logstash-{date},logstash-{bdate}'.format(date=torday,bdate=yesterday)
    index_flag = es.indices.exists(es_index)
    if not index_flag:
        es.indices.create(es_index)
    #设置获取间隔多长时间的数据规则
    data = {
        "query": {
            "bool": {
                # 指定要匹配的字符，这里是查找所有数据
                "must": {"match_all": {}},
                "filter": {
                    "range": {"@timestamp": {
                        'gt': '',
                    }
                    }
                }
            }
        }
    }
    data['query']['bool']['filter']['range']['@timestamp']['gt']='now-{data}m'.format(data=time)
    #获取日志数据,获取当前时间
    date_now = datetime.datetime.now()
    date_now = date_now.strftime("%Y-%m-%d %H:%M:%S")
    page = es.search(
        index=es_index,
        # scroll='5s',
        size=10000,
        search_type='dfs_query_then_fetch',
        body=data
    )
    #判断是否存在日志，存在获取page['hits']['hits']否则no log
    if page['hits']['total']>0:
        data_log = page['hits']['hits']
    else:
        data_log = {'_source': {'message': ['nolog']}}
    #去数据库获取对应间隔时间需要分析的所有规则
    db_conn = DbConnect()
    cursor = db_conn.connect()
    sql = """
        select rule_name,rule_content,rule_condtion,rule_price,rule_id 
        from warning_rule  where rule_time=%s
    """
    cursor.execute(sql,[time])
    ret_list=cursor.fetchall()
    #创建进程池，并且把日志数据和规则和当前时间都传进分析函数
    pool = ThreadPoolExecutor(5)
    for rule in ret_list:
        pool.submit(analyze_log(rule,data_log,date_now))
    pool.shutdown(wait=True)
