#!/usr/bin/python

import util
import collectd

TAG_LIST_1 = ['keyspace', 'shard', 'type']
TAG_LIST_2 = ['type']
TAG_LIST_3 = ['method', 'keyspace', 'shard', 'type']
TAG_LIST_4 = ['method', 'keyspace', 'type']
TAG_LIST_5 = ['method']
TAG_LIST_6 = ['table', 'type']
TAG_LIST_7 = ['table', 'plan', 'id', 'user']
TAG_LIST_8 = ['table', 'user', 'type']
TAG_LIST_9 = ['user', 'type']
TAG_LIST_10 = ['table']
TAG_LIST_11 = ['method','type']

VITESS_CONFIG = {
    'Host':           'localhost',
    'Port':           15001,
}

def process_data(json_data):
    epoch_time = util.get_epoch_time()

    util.publish_metric(epoch_time, "vitess.appConnPoolAvailable", json_data['AppConnPoolAvailable']
                        , 'gauge', None)
    util.publish_metric(epoch_time, "vitess.appConnPoolCapacity", json_data['AppConnPoolCapacity']
                        , 'gauge', None)
    util.publish_metric(epoch_time, "vitess.appConnPoolWaitCount", json_data['AppConnPoolWaitCount']
                        , 'gauge', None)
    if json_data['AppConnPoolWaitCount'] > 0:
        util.publish_metric(epoch_time, "vitess.appConnPoolAvgWaitTime"
                            , (json_data['AppConnPoolWaitTime']/1000000.0)/json_data['AppConnPoolWaitCount']
                            , 'gauge', None)
    else:
        util.publish_metric(epoch_time, "vitess.appConnPoolAvgWaitTime", 0, 'gauge', None)

    util.publish_metric(epoch_time, "vitess.connPoolAvailable", json_data['ConnPoolAvailable'],'gauge', None)
    util.publish_metric(epoch_time, "vitess.connPoolCapacity", json_data['ConnPoolCapacity'],'gauge', None)
    util.publish_metric(epoch_time, "vitess.connPoolWaitCount", json_data['ConnPoolWaitCount'],'gauge', None)
    if json_data['ConnPoolWaitCount'] > 0:
        util.publish_metric(epoch_time, "vitess.connPoolAvgWaitTime"
                            , (json_data['ConnPoolWaitTime']/1000000.0)/json_data['ConnPoolWaitCount'],'gauge', None)
    else:
        util.publish_metric(epoch_time, "vitess.connPoolAvgWaitTime", 0,'gauge', None)

    util.publish_metric(epoch_time, "vitess.dbaConnPoolAvailable", json_data['DbaConnPoolAvailable']
                        ,'gauge', None)
    util.publish_metric(epoch_time, "vitess.dbaConnPoolCapacity", json_data['DbaConnPoolCapacity']
                        ,'gauge', None)
    util.publish_metric(epoch_time, "vitess.dbaConnPoolWaitCount", json_data['DbaConnPoolWaitCount']
                        ,'gauge', None)
    if json_data['DbaConnPoolWaitCount'] > 0:
        util.publish_metric(epoch_time, "vitess.dbaConnPoolAvgWaitTime"
                            , (json_data['DbaConnPoolWaitTime']/1000000.0)/json_data['DbaConnPoolWaitCount'],'gauge', None)
    else:
        util.publish_metric(epoch_time, "vitess.dbaConnPoolAvgWaitTime", 0,'gauge', None)

    util.publish_metric(epoch_time, "vitess.streamConnPoolAvailable"
                        , json_data['StreamConnPoolAvailable'],'gauge', None)
    util.publish_metric(epoch_time, "vitess.streamConnPoolCapacity"
                        , json_data['StreamConnPoolCapacity'],'gauge', None)
    util.publish_metric(epoch_time, "vitess.streamConnPoolWaitCount"
                        , json_data['StreamConnPoolWaitCount'],'gauge', None)
    if json_data['StreamConnPoolWaitCount'] > 0:
        util.publish_metric(epoch_time, "vitess.streamConnPoolAvgWaitTime"
                            , (json_data['StreamConnPoolWaitTime']/1000000.0)/json_data['StreamConnPoolWaitCount'],'gauge', None)
    else:
        util.publish_metric(epoch_time, "vitess.streamConnPoolAvgWaitTime", 0,'gauge', None)

    util.publish_metric(epoch_time, "vitess.transactionPoolAvailable"
                        , json_data['TransactionPoolAvailable'],'gauge', None)
    util.publish_metric(epoch_time, "vitess.transactionPoolCapacity"
                        , json_data['TransactionPoolCapacity'],'gauge', None)
    util.publish_metric(epoch_time, "vitess.transactionPoolWaitCount"
                        , json_data['TransactionPoolWaitCount'],'gauge', None)
    if json_data['TransactionPoolWaitCount'] > 0:
        util.publish_metric(epoch_time, "vitess.transactionPoolAvgWaitTime"
                            , (json_data['TransactionPoolWaitTime']/1000000.0)/json_data['TransactionPoolWaitCount'],'gauge', None)
    else:
        util.publish_metric(epoch_time, "vitess.transactionPoolAvgWaitTime", 0,'gauge', None)

    util.create_metric(epoch_time, "vitess.errors", json_data['Errors'], TAG_LIST_2)
    util.create_metric(epoch_time, "vitess.healthcheckErrors", json_data['HealthcheckErrors']
                       , TAG_LIST_1)
    util.create_metric(epoch_time, "vitess.infoErrors", json_data['InfoErrors'], TAG_LIST_2)
    util.create_metric(epoch_time, "vitess.internalErrors", json_data['InternalErrors'], TAG_LIST_2)
    util.create_metric(epoch_time, "vitess.kills", json_data['Kills'], TAG_LIST_2)

    util.publish_metric(epoch_time, "vitess.mysql.totalCount", json_data['Mysql']['TotalCount'],'gauge', None)
    util.create_metric_histogram(epoch_time, "vitess.mysql.count", json_data['Mysql'], TAG_LIST_5)

    util.publish_metric(epoch_time, "vitess.mysqlApp.totalCount", json_data['MysqlApp']['TotalCount']
                        ,'gauge', None)
    util.create_metric_histogram(epoch_time, "vitess.mysqlApp.count", json_data['MysqlApp']
                                 , TAG_LIST_5)

    util.publish_metric(epoch_time, "vitess.mysqlDba.totalCount", json_data['MysqlDba']['TotalCount']
                        ,'gauge', None)
    util.create_metric_histogram(epoch_time, "vitess.mysqlDba.count", json_data['MysqlDba']
                                 , TAG_LIST_5)

    util.publish_metric(epoch_time, "vitess.queries.totalCount", json_data['Queries']['TotalCount']
                        ,'gauge', None)
    util.create_metric_histogram(epoch_time, "vitess.queries.count", json_data['Queries'], TAG_LIST_2)

    util.publish_metric(epoch_time, "vitess.transactions.totalCount"
                        , json_data['Transactions']['TotalCount'],'gauge', None)
    util.create_metric_histogram(epoch_time, "vitess.transactions.count", json_data['Transactions']
                                 , TAG_LIST_2)

    util.publish_metric(epoch_time, "vitess.waits.totalCount", json_data['Waits']['TotalCount'],'gauge', None)
    util.create_metric_histogram(epoch_time, "vitess.waits.count", json_data['Waits'], TAG_LIST_2)

    util.publish_metric(epoch_time, "vitess.queryCacheCapacity", json_data['QueryCacheCapacity'],'gauge', None)
    util.publish_metric(epoch_time, "vitess.queryCacheLength", json_data['QueryCacheLength'],'gauge', None)
    util.create_metric(epoch_time, "vitess.queryCounts", json_data['QueryCounts'], TAG_LIST_6)
    util.create_metric(epoch_time, "vitess.queryErrorCounts", json_data['QueryErrorCounts']
                       , TAG_LIST_6)
    util.create_metric(epoch_time, "vitess.queryRowCounts", json_data['QueryRowCounts'], TAG_LIST_6)
    util.create_metric_avg(epoch_time, "vitess.queryAvgTime", json_data['QueryTimesNs']
                           , json_data['QueryRowCounts'], TAG_LIST_6)

    util.publish_metric(epoch_time, "vitess.results.count", json_data['Results']['Count'],'gauge', None)

    util.create_metric(epoch_time, "vitess.streamlogDelivered", json_data['StreamlogDelivered']
                       , TAG_LIST_11)
    util.create_metric(epoch_time, "vitess.streamlogDeliveryDroppedMessages"
                       , json_data['StreamlogDeliveryDroppedMessages'], TAG_LIST_2)
    util.create_metric(epoch_time, "vitess.streamlogSend", json_data['StreamlogSend'], TAG_LIST_2)

    util.create_metric(epoch_time, "vitess.tableACLAllowed", json_data['TableACLAllowed'], TAG_LIST_7)
    util.create_metric(epoch_time, "vitess.tableACLDenied", json_data['TableACLDenied'], TAG_LIST_7)
    util.create_metric(epoch_time, "vitess.tableACLPseudoDenied", json_data['TableACLPseudoDenied']
                       , TAG_LIST_7)
    util.publish_metric(epoch_time, "vitess.tableACLExemptCount", json_data['TableACLExemptCount']
                        , 'gauge', None)

    util.create_metric(epoch_time, "vitess.dataFree", json_data['DataFree'], TAG_LIST_10)
    util.create_metric(epoch_time, "vitess.dataLength", json_data['DataLength'], TAG_LIST_10)
    util.create_metric(epoch_time, "vitess.tableRows", json_data['TableRows'], TAG_LIST_10)

    util.publish_metric(epoch_time, "vitess.tabletState", json_data['TabletState'],'gauge', None)

    util.create_metric(epoch_time, "vitess.userTableQueryCount", json_data['UserTableQueryCount']
                       , TAG_LIST_8)
    util.create_metric_avg(epoch_time, "vitess.userTableQueryAvgTime"
                           , json_data['UserTableQueryTimesNs'], json_data['UserTableQueryCount']
                           , TAG_LIST_8)
    util.create_metric(epoch_time, "vitess.userTransactionCount", json_data['UserTransactionCount']
                       , TAG_LIST_9)
    util.create_metric_avg(epoch_time, "vitess.userTransactionAvgTime"
                           , json_data['UserTransactionTimesNs'], json_data['UserTransactionCount']
                           , TAG_LIST_9)

def read_callback():
    url = "http://" + VITESS_CONFIG['Host'] + \
          ":" + str(VITESS_CONFIG['Port']) + "/debug/vars"
    json_data = util.get_json_data(url)
    process_data(json_data)

def configure_callback(conf):

    global VITESS_CONFIG
    for node in conf.children:
        if node.key in VITESS_CONFIG:
            VITESS_CONFIG[node.key] = node.values[0]

    VITESS_CONFIG['Port']    = int(VITESS_CONFIG['Port'])

if __name__ == '__main__':
    collectd.register_read(read_callback)
    collectd.register_config(configure_callback)

else:
    import collectd
    collectd.register_config(configure_callback)
    collectd.register_read(read_callback)
