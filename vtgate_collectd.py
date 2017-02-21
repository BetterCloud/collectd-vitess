#!/usr/bin/python

#!/usr/bin/python

import time
import util
import mock

NAME = 'vtgate'

class Vtgate(util.BaseCollector):
    def __init__(self, collectd, json_provider=None, verbose=False, interval=None):
        super(Vtgate, self).__init__(collectd, NAME, 15001, json_provider, verbose, interval)

    def configure_callback(self, conf):
        super(Vtgate, self).configure_callback(conf)

        for node in conf.children:
            pass

        self.register_read_callback()

    def process_data(self, json_data):
        # Current connections and total accepted
        self.process_metric(json_data, 'ConnAccepted', 'counter')
        self.process_metric(json_data, 'ConnCount', 'gauge')

        # healthcheck metrics, both errors and connections
        hc_tags = ['keyspace', 'shard', 'type']
        self.process_metric(json_data, 'HealthcheckErrors', 'counter', parse_tags=hc_tags)
        self.process_metric(json_data, 'HealthcheckConnections', 'gauge', parse_tags=hc_tags)

        # GC Stats
        memstats = json_data['memstats']
        self.process_metric(memstats, 'GCCPUFraction', 'gauge', prefix='GC.', alt_name='CPUFraction')
        self.process_metric(memstats, 'PauseTotalNs', 'gauge', prefix='GC.')

        # We should endeavor to have 0 statements that are unfriendly to filtered replication for any keyspaces that want to be sharded
        self.process_metric(json_data, 'FilteredReplicationUnfriendlyStatementsCount', 'counter')

        self.process_rates(json_data, 'QPSByDbType', 'DbType')
        self.process_rates(json_data, 'QPSByKeyspace', 'Keyspace')
        self.process_rates(json_data, 'QPSByOperation', 'Operation')
        self.process_rates(json_data, 'ErrorsByDbType', 'DbType')
        self.process_rates(json_data, 'ErrorsByKeyspace', 'Keyspace')
        self.process_rates(json_data, 'ErrorsByOperation', 'Operation')

        # Subtracting VtgateApi from VttabletCall times below should allow seeing what overhead vtgate adds
        parse_tags = ['Operation', 'Keyspace', 'DbType']
        self.process_timing_data(json_data, 'VtgateApi', parse_tags=parse_tags)
        self.process_metric(json_data, 'VtgateApiErrorCounts', 'counter', parse_tags=parse_tags)

        parse_tags = ['type']
        self.process_metric(json_data, 'VtgateInfoErrorCounts', 'counter', parse_tags=parse_tags)
        self.process_metric(json_data, 'VtgateInternalErrorCounts', 'counter', parse_tags=parse_tags)
        
        parse_tags = ['Operation', 'Keyspace', 'ShardName', 'DbType']
        self.process_metric(json_data, 'VttabletCallErrorCount', 'counter', parse_tags=parse_tags)
        self.process_timing_data(json_data, 'VttabletCall', parse_tags=parse_tags)
        
        parse_tags = ['Keyspace', 'ShardName']
        self.process_metric(json_data, 'BufferUtilizationSum', 'counter', parse_tags=parse_tags)
        self.process_metric(json_data, 'BufferStarts', 'counter', parse_tags=parse_tags)
        self.process_metric(json_data, 'BufferRequestsBuffered', 'counter', parse_tags=parse_tags)
        self.process_metric(json_data, 'BufferRequestsDrained', 'counter', parse_tags=parse_tags)

        parse_tags = ['Keyspace', 'ShardName', 'Reason']
        self.process_metric(json_data, 'BufferRequestsEvicted', 'counter', parse_tags=parse_tags)
        self.process_metric(json_data, 'BufferRequestsSkipped', 'counter', parse_tags=parse_tags)

    def process_rates(self, json_data, metric_name, tag_name):
        rates = json_data[metric_name]

        for key, values in rates.items():
            if key.lower() == "all":
                continue
            oneMin = values[-1]
            fiveMin = sum(values[-5:])/5
            fifteenMin = sum(values[-15:])/15

            tags = dict()
            tags[tag_name] = key
            self.emitter.emit("vitess.%s.1min" % metric_name, oneMin, 'gauge', tags)
            self.emitter.emit("vitess.%s.5min" % metric_name, fiveMin, 'gauge', tags)
            self.emitter.emit("vitess.%s.15min" % metric_name, fifteenMin, 'gauge', tags)

if __name__ == '__main__':
    util.run_local(NAME, Vtgate)
else:
    import collectd
    vt = Vtgate(collectd)
    collectd.register_config(vt.configure_callback)