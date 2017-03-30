#!/usr/bin/python

import time
import util

NAME = 'vttablet'

class Vttablet(util.BaseCollector):
    def __init__(self, collectd, json_provider=None, verbose=False, interval=None):
        super(Vttablet, self).__init__(collectd, NAME, 15101, json_provider, verbose, interval)
        self.include_per_user_timings = True
        self.include_streamlog_stats = True
        self.include_acl_stats = True
        self.include_results_histogram = True
        self.include_reparent_timings = True

    def configure_callback(self, conf):
        super(Vttablet, self).configure_callback(conf)
        for node in conf.children:
            if node.key == 'IncludeResultsHistogram':
                self.include_results_histogram = util.boolval(node.values[0])
            elif node.key == 'IncludeTimingsPerUser':
                self.include_per_user_timings = util.boolval(node.values[0])
            elif node.key == 'IncludeStreamLog':
                self.include_streamlog_stats = util.boolval(node.values[0])
            elif node.key == 'IncludeACLStats':
                self.include_acl_stats = util.boolval(node.values[0])
            elif node.key == 'IncludeExternalReparentTimings':
                self.include_reparent_timings = util.boolval(node.values[0])

        self.register_read_callback()

    def process_data(self, json_data):
        # Current connections and total accepted
        self.process_metric(json_data, 'ConnAccepted', 'counter')
        self.process_metric(json_data, 'ConnCount', 'gauge')

        # Health-related metrics.
        # TabletState is an integer mapping to one of SERVING (2), NOT_SERVING (0, 1, 3), or SHUTTING_DOWN (4)
        self.process_metric(json_data, 'TabletState', 'gauge')
        # Report on whether this is a master
        self.process_metric(json_data, 'TabletType', 'gauge', alt_name='IsMaster', transformer=lambda val: 1 if val.lower() == 'master' else 0)
        self.process_metric(json_data, 'HealthcheckErrors', 'counter', parse_tags=['keyspace', 'shard', 'type'])

        # GC Stats
        memstats = json_data['memstats']
        self.process_metric(memstats, 'GCCPUFraction', 'gauge', prefix='GC.', alt_name='CPUFraction')
        self.process_metric(memstats, 'PauseTotalNs', 'gauge', prefix='GC.')

        # Tracking usage of the various connection pools
        self.process_pool_data(json_data, 'Conn')
        self.process_pool_data(json_data, 'AppConn')
        self.process_pool_data(json_data, 'DbaConn')
        self.process_pool_data(json_data, 'StreamConn')
        self.process_pool_data(json_data, 'Transaction')

        # If enabled, track histogram of number of results returned from user queries
        if self.include_results_histogram:
            self.process_histogram(json_data, 'Results')

        # Counters tagged by type, for tracking various error modes of the vttablet
        for metric in ['Errors', 'InfoErrors', 'InternalErrors', 'Kills']:
            self.process_metric(json_data, metric, 'counter', parse_tags=['type'])

        # Counters tagged by table and type, for tracking counts of the various query types, times, and ways in which a query can fail
        # all broken down by table
        for metric in ['QueryCounts', 'QueryErrorCounts', 'QueryRowCounts', 'QueryTimesNs']:
            alt_name = 'QueryTimes' if metric == 'QueryTimeNs' else None
            transformer = util.nsToMs if metric == 'QueryTimesNs' else None
            self.process_metric(json_data, metric, 'counter', alt_name=alt_name, parse_tags=['table', 'type'], transformer=transformer)

        # Tracks data from information_schema about the size of tables
        for metric in ['DataFree', 'DataLength', 'IndexLength', 'TableRows']:
            self.process_metric(json_data, metric, 'gauge', parse_tags=['table'])

        # Tracks counts and timings of user queries by user, table, and type
        user_table_tags = ['table', 'user', 'type']
        self.process_metric(json_data, 'UserTableQueryCount', 'counter', parse_tags=user_table_tags)
        self.process_metric(json_data, 'UserTableQueryTimesNs', 'counter', alt_name='UserTableQueryTime', parse_tags=user_table_tags, transformer=util.nsToMs)

        # Tracks counts and timings of user transactions by user and type
        user_tx_tags = ['user', 'type']
        self.process_metric(json_data, 'UserTransactionCount', 'counter', parse_tags=user_tx_tags)
        self.process_metric(json_data, 'UserTransactionTimesNs', 'counter', alt_name='UserTransactionTime', parse_tags=user_tx_tags, transformer=util.nsToMs)

        # Tracks a variety of metrics for timing of the various layers of execution
        # MySQL is how long it takes to actually execute in MySQL. While Queries is the total time with vitess overhead
        # Waits tracks instances where we are able to consolidate identical queries while waiting for a connection
        self.process_timing_data(json_data, 'MySQL')
        self.process_timing_data(json_data, 'Queries')
        self.process_timing_data(json_data, 'Transactions')
        self.process_timing_data(json_data, 'Waits')
        if self.include_reparent_timings:
            self.process_timing_data(json_data, 'ExternalReparents')

        # MySQL timings above, broken down by user
        if self.include_per_user_timings:
            self.process_timing_data(json_data, 'MysqlAllPrivs')
            self.process_timing_data(json_data, 'MysqlApp')
            self.process_timing_data(json_data, 'MysqlDba')

        # Track usage of Vitess' query PLAN cache
        self.process_metric(json_data, 'QueryCacheCapacity', 'gauge', alt_name='QueryPlanCacheCapacity')
        self.process_metric(json_data, 'QueryCacheLength', 'gauge', alt_name='QueryPlanCacheLength')

        # Tracks messages sent and success of delivery for the stream log
        if self.include_streamlog_stats:
            self.process_metric(json_data, 'StreamlogSend', 'counter', parse_tags=['log'])
            parse_tags = ['log', 'subscriber']
            self.process_metric(json_data, 'StreamlogDelivered', 'counter', parse_tags=parse_tags)
            self.process_metric(json_data, 'StreamlogDeliveryDroppedMessages', 'counter', parse_tags=parse_tags)

        # Tracks the impact of ACLs on user queries
        if self.include_acl_stats:
            acl_tags = ['table', 'plan', 'id', 'user']
            self.process_metric(json_data, 'TableACLAllowed', 'counter', parse_tags=acl_tags)
            self.process_metric(json_data, 'TableACLDenied', 'counter', parse_tags=acl_tags)
            self.process_metric(json_data, 'TableACLPseudoDenied', 'counter', parse_tags=acl_tags)
            # Super users are exempt and are tracked by this
            self.process_metric(json_data, 'TableACLExemptCount', 'counter')

    def process_pool_data(self, json_data, pool_name):
        self.process_metric(json_data, '%sPoolAvailable' % pool_name, 'gauge')
        self.process_metric(json_data, '%sPoolCapacity' % pool_name, 'gauge')
        self.process_metric(json_data, '%sPoolWaitCount' % pool_name, 'counter')
        self.process_metric(json_data, '%sPoolWaitTime' % pool_name, 'counter', transformer=util.nsToMs)

if __name__ == '__main__':
    util.run_local(NAME, Vttablet)
else:
    import collectd
    vt = Vttablet(collectd)
    collectd.register_config(vt.configure_callback)
