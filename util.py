#!/usr/bin/python

import sys
import time
import urllib2
import json
import os
import collectd
import logging

PREFIX = "vitess"

class CollectdLogHandler(logging.Handler):
    """Log handler to forward statements to collectd
    A custom log handler that forwards log messages raised
    at level debug, info, notice, warning, and error
    to collectd's built in logging.  Suppresses extraneous
    info and debug statements using a "verbose" boolean

    Inherits from logging.Handler

    Arguments
        plugin -- name of the plugin (default 'unknown')
        verbose -- enable/disable verbose messages (default False)
    """
    def __init__(self, plugin="vitess", verbose=False):
        """Initializes CollectdLogHandler
        Arguments
            plugin -- string name of the plugin (default 'unknown')
            verbose -- enable/disable verbose messages (default False)
        """
        self.verbose = verbose
        self.plugin = plugin
        logging.Handler.__init__(self, level=logging.NOTSET)

    def emit(self, record):
        """
        Emits a log record to the appropraite collectd log function

        Arguments
        record -- str log record to be emitted
        """
        try:
            if record.msg is not None:
                if record.levelname == 'ERROR':
                    collectd.error('%s : %s' % (self.plugin, record.msg))
                elif record.levelname == 'WARNING':
                    collectd.warning('%s : %s' % (self.plugin, record.msg))
                elif record.levelname == 'NOTICE':
                    collectd.notice('%s : %s' % (self.plugin, record.msg))
                elif record.levelname == 'INFO' and self.verbose is True:
                    collectd.info('%s : %s' % (self.plugin, record.msg))
                elif record.levelname == 'DEBUG' and self.verbose is True:
                    collectd.debug('%s : %s' % (self.plugin, record.msg))
        except Exception as e:
            collectd.warning(('{p} [ERROR]: Failed to write log statement due '
                              'to: {e}').format(p=self.plugin,
                                                e=e
                                                ))

class CollectdLogger(logging.Logger):
    """Logs all collectd log levels via python's logging library
    Custom python logger that forwards log statements at
    level: debug, info, notice, warning, error

    Inherits from logging.Logger

    Arguments
    name -- name of the logger
    level -- log level to filter by
    """
    def __init__(self, name, level=logging.NOTSET):
        """Initializes CollectdLogger

        Arguments
        name -- name of the logger
        level -- log level to filter by
        """
        logging.Logger.__init__(self, name, level)
        logging.addLevelName(25, 'NOTICE')

    def notice(self, msg):
        """Logs a 'NOTICE' level statement at level 25

        Arguments
        msg - log statement to be logged as 'NOTICE'
        """
        self.log(25, msg)


# Set up logging
logging.setLoggerClass(CollectdLogger)
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
logger.propagate = False
handle = CollectdLogHandler(PREFIX)
logger.addHandler(handle)

def log(message):
    logger.info(message)

def entry(method_name):
    logger.debug("In: " + method_name)


def leave(method_name):
    logger.debug("Out: " + method_name)

def get_epoch_time():
    return int(time.time())


def get_json_data(url):
    response = None
    try:
        logger.info('Fetching api information from: %s' % url)
        request = urllib2.Request(url)
        response = urllib2.urlopen(request, timeout=10)
        logger.debug('Raw api response: %s' % response)
        return json.load(response)
    except (urllib2.URLError, urllib2.HTTPError), e:
        logger.error('Error connecting to %s - %r : %s' %
                     (url, e, e))
        return None
    finally:
        if response is not None:
            response.close()

def create_metric(epoch_time, metric_name, data, tag_list):
    method_name = "create_metric for " + metric_name
    entry(method_name)

    for key in data.keys():
        tags = extract_tags(key, '.', tag_list)
        if tags != "-1":
            publish_metric(epoch_time, metric_name, data[key], 'gauge', tags)

    leave(method_name)


def create_metric_histogram(epoch_time, metric_name, data, tag_list):
    method_name = "create_metric_histogram for " + metric_name
    entry(method_name)

    histogram_data = data['Histograms']
    for key in histogram_data.keys():
        tags = extract_tags(key, '.', tag_list)
        if tags != "-1":
            publish_metric(epoch_time, metric_name, histogram_data[key]['Count'], 'gauge', tags)

    leave(method_name)


def create_metric_avg(epoch_time, metric_name, data_time, data_count, tag_list):
    method_name = "create_metric for " + metric_name
    entry(method_name)

    for key in data_time.keys():
        tags = extract_tags(key, '.', tag_list)
        if tags != "-1":
            if data_count[key] != 0:
                publish_metric(epoch_time, metric_name, (data_time[key]/1000000.0)/data_count[key], 'gauge', tags)
            else:
                publish_metric(epoch_time, metric_name, 0.0, 'gauge', tags)

    leave(method_name)


def extract_tags(key, split_char, tag_list):
    tag_data = key.split(split_char)
    if len(tag_data) != len(tag_list):
        logger.error("extract_tags: Data not as expected for " + key + " tag list: "
                     + str(tag_list))
        return "-1"
    else:
        tags = {}
        i = 0
        for tag in tag_data:
            tags[tag_list[i]] = tag.replace(" ", "_")
            i += 1
        return tags


def publish_metric(epoch_time, metric_name, metric_value, type, tags):
    method_name = "publish_metric for " + metric_name
    entry(method_name)
    tag_str = ""
    if tags:
        total_keys = len(tags)
        i = 0

        for key in tags.keys():
            tag_str += key + "=" + tags[key]
            i += 1
            tag_str += " "
    val               = collectd.Values(plugin='vitess', plugin_instance=metric_name)
    val.type          = type
    val.type_instance = tag_str
    val.values        = [metric_value]
    val.dispatch()
    leave(method_name)
