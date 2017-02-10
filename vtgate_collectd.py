#!/usr/bin/python

import util
import collectd

TAG_LIST_1 = ['keyspace', 'shard', 'type']
TAG_LIST_2 = ['type']
TAG_LIST_3 = ['method', 'keyspace', 'shard', 'type']
TAG_LIST_4 = ['method', 'keyspace', 'type']

VITESS_CONFIG = {
    'Host':           'localhost',
    'Port':           15001,
}

def process_data(json_data):
    epoch_time = util.get_epoch_time()

    util.create_metric(epoch_time, "vitess.healthcheckConnections", json_data['HealthcheckConnections']
                       , TAG_LIST_1)

    util.create_metric(epoch_time, "vitess.healthcheckErrors", json_data['HealthcheckErrors']
                       , TAG_LIST_1)

    util.create_metric(epoch_time, "vitess.vtgateApiErrorCounts", json_data['VtgateApiErrorCounts']
                       , TAG_LIST_4)

    util.create_metric(epoch_time, "vitess.vtgateApiRowsReturned", json_data['VtgateApiRowsReturned']
                       , TAG_LIST_4)

    util.create_metric(epoch_time, "vitess.vtgateInfoErrorCounts", json_data['VtgateInfoErrorCounts']
                       , TAG_LIST_2)

    util.create_metric(epoch_time, "vitess.vtgateInternalErrorCounts"
                       , json_data['VtgateInternalErrorCounts'], TAG_LIST_2)

    util.create_metric(epoch_time, "vitess.vttabletCallErrorCount", json_data['VttabletCallErrorCount']
                       , TAG_LIST_3)

    util.publish_metric(epoch_time, "vitess.vtgateApi.totalCount", json_data['VtgateApi']['TotalCount']
                        , 'gauge', None)

    util.publish_metric(epoch_time, "vitess.vtgateApi.latency", (long(json_data['VtgateApi']['TotalTime'])/(long(json_data['VtgateApi']['TotalCount']) * 1000000000))
                        ,'gauge', None)

    util.create_metric_histogram(epoch_time, "vitess.vtgateApi.count", json_data['VtgateApi']
                                 , TAG_LIST_4)

    util.publish_metric(epoch_time, "vitess.vttabletCall.totalCount"
                        , json_data['VttabletCall']['TotalCount'], 'gauge', None)

    util.create_metric_histogram(epoch_time, "vitess.vttabletCall.count", json_data['VttabletCall']
                                 , TAG_LIST_3)

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
