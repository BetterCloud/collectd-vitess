#!/usr/bin/python

import abc
import sys
import time
import urllib2
import json
import os
import logging
import re
import mock

class CollectdLogHandler(logging.Handler):
    """Log handler to forward statements to collectd
    A custom log handler that forwards log messages raised
    at level debug, info, notice, warning, and error
    to collectd's built in logging.  Suppresses extraneous
    info and debug statements using a "verbose" boolean

    Inherits from logging.Handler

    Arguments
        collectd -- the collectd object to use
        plugin -- name of the plugin (default 'unknown')
        verbose -- enable/disable verbose messages (default False)
    """
    def __init__(self, collectd, plugin="vitess", verbose=False):
        """Initializes CollectdLogHandler
        Arguments
            collectd -- the collectd object to use
            plugin -- string name of the plugin (default 'unknown')
            verbose -- enable/disable verbose messages (default False)
        """
        self.collectd = collectd
        self.verbose = verbose
        self.plugin = plugin
        logging.Handler.__init__(self, level=logging.NOTSET)

    def register(self):
        logger.addHandler(self)

    def emit(self, record):
        """
        Emits a log record to the appropraite collectd log function

        Arguments
        record -- str log record to be emitted
        """
        try:
            if record.msg is not None:
                if record.levelname == 'ERROR':
                    self.collectd.error('%s : %s' % (self.plugin, record.msg))
                elif record.levelname == 'WARNING':
                    self.collectd.warning('%s : %s' % (self.plugin, record.msg))
                elif record.levelname == 'NOTICE':
                    self.collectd.notice('%s : %s' % (self.plugin, record.msg))
                elif record.levelname == 'INFO' and self.verbose is True:
                    self.collectd.info('%s : %s' % (self.plugin, record.msg))
                elif record.levelname == 'DEBUG' and self.verbose is True:
                    self.collectd.debug('%s : %s' % (self.plugin, record.msg))
        except Exception as e:
            self.collectd.warning(('{p} [ERROR]: Failed to write log statement due '
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

def log(message):
    logger.info(message)

def entry(method_name):
    logger.debug("In: " + method_name)


def leave(method_name):
    logger.debug("Out: " + method_name)


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

def extract_tagged_values(data, name, key_split_char='.', tag_list=None):
    values = data[name]
    if not tag_list:
        return [(dict(), value) for value in values.values()]

    if type(values) is not dict:
        return _extract_tagged_value(name, values, key_split_char, tag_list)

    result = []
    for key, value in values.items():
        result.append(_extract_tagged_value(key, value, key_split_char, tag_list))
    return result

def _extract_tagged_value(name, value, key_split_char, tag_list):
    return (_extract_tags(name, key_split_char, tag_list), value)

def _extract_tags(name, key_split_char='.', tag_list=None):
    if not tag_list:
        return dict()
    tag_data = [x.replace(" ", "_") for x in name.split(key_split_char)]
    if len(tag_data) != len(tag_list):
        raise Exception("Data not as expected for " + name + " tag list: " + str(tag_list))

    tags = dict(zip(tag_list, tag_data))
    return tags


def default_extractor(data, name):
    return [(dict(), data[name])]

def nsToMs(ns):
    return ns / 1000000.0

def boolval(val):
        return val.__str__().lower() == 'true'

def upperSnakeToCamel(val):
    if re.match(r'^[A-Z_]+$', val):
        return val.title().replace('_', '')
    return val

class JsonProvider(object):
    __metaclass__ = abc.ABCMeta

    @abc.abstractmethod
    def get_json(self):
        """
        Return json data for parsing
        """
        return

class UrlJsonProvider(JsonProvider):
    def __init__(self, host="localhost", port="15101", path="/debug/vars"):
        self.host = host
        self.port = port
        self.path = path

    def get_json(self):
        url = "http://%s:%s%s" % (self.host, self.port, self.path)
        return self._fetch(url)

    def _fetch(self, url):
        response = None
        try:
            logger.info('Fetching api information from: %s' % url)
            request = urllib2.Request(url)
            response = urllib2.urlopen(request, timeout=10)
            logger.debug('Raw api response: %s' % response)
            return json.load(response)
        except (urllib2.URLError, urllib2.HTTPError), e:
            logger.error('Error connecting to %s - %r : %s' % (url, e, e))
            return None
        finally:
            if response:
                response.close()

class FileJsonProvider(JsonProvider):
    def __init__(self, path):
        self.path = path

    def get_json(self):
        with open(self.path, "r") as f:
            return json.load(f)

class MetricEmitter(object):
    def __init__(self, collectd, plugin_instance, plugin='vitess'):
        self.collectd = collectd
        self.plugin_instance = plugin_instance
        self.plugin = plugin

    def emit(self, metric_name, metric_value, type, tags=None):
        method_name = "emit_metric for " + metric_name
        entry(method_name)
        self._emit(metric_name, metric_value, type, tags)
        leave(method_name)

    def _emit(self, metric_name, metric_value, type, tags):
        tag_str = self._generate_tags_str(tags)
        val = self.collectd.Values(plugin=self.plugin, plugin_instance=self.plugin_instance)
        val.type = type
        val.type_instance = "%s.%s.%s%s" % (self.plugin, self.plugin_instance, metric_name, tag_str)
        val.values = [metric_value]
        val.dispatch()

    def _generate_tags_str(self, tags):
        if tags:
            return "[%s]" % ','.join(["%s=%s" % (x, y) for x, y in tags.items()])
        return ""

class BaseCollector(object):
    def __init__(self, collectd, name, default_port, json_provider=None, verbose=False, interval=None):
        self.collectd = collectd
        self.name = name
        self.default_port = default_port
        self.json_provider = json_provider
        self.verbose = verbose
        self.interval = interval
        self.emitter = MetricEmitter(self.collectd, self.name)
        self.include_timing_histograms = True

    def configure_callback(self, conf):
        json_provider = UrlJsonProvider(port=self.default_port)
        for node in conf.children:
            if node.key == 'URL':
                json_provider.url = node.values[0]
            elif node.key == 'Port':
                json_provider.port = node.values[0]
            elif node.key == 'Path':
                json_provider.path = node.values[0]
            elif node.key == 'Interval':
                self.interval = int(node.values[0])
            elif node.key == 'Verbose':
                self.verbose = boolval(node.values[0])
            elif node.key == 'IncludeTimingHistograms':
                self.include_timing_histograms = util.boolval(node.values[0])

        handler = CollectdLogHandler(self.collectd, self.name, self.verbose)
        handler.register()

        self.json_provider = json_provider

    def register_read_callback(self):
        if self.interval:
            self.collectd.register_read(self.read_callback, interval=self.interval)
        else:
            self.collectd.register_read(self.read_callback)

    def read_callback(self):
        json = self.json_provider.get_json()
        self.process_data(json)

    def process_timing_data(self, json_data, timing_name, parse_tags=None):
        timing_values = json_data[timing_name]
        self.process_metric(timing_values, 'TotalCount', 'counter', prefix=timing_name)
        self.process_metric(timing_values, 'TotalTime', 'counter', prefix=timing_name, transformer=nsToMs)

        for key, histogram in timing_values['Histograms'].items():
            if parse_tags:
                tags = _extract_tags(key, tag_list=parse_tags)
                prefix = timing_name
            else:
                tags = None
                prefix = "%s%s" % (timing_name, upperSnakeToCamel(key))
            self.process_metric(histogram, 'Count', 'counter', prefix=prefix, base_tags=tags)
            self.process_metric(histogram, 'Time', 'counter', prefix=prefix, base_tags=tags, transformer=nsToMs)

            if self.include_timing_histograms:
                def nsKeysToMs(key):
                    if key.isdigit():
                        return "%d" % nsToMs(long(key))
                    return key

                self.process_histogram(timing_values['Histograms'], key, prefix=timing_name, alt_name="", suffix="Time", tags=tags, key_transformer=nsKeysToMs)

    def process_histogram(self, json_data, metric_name, prefix="", alt_name=None, suffix="", key_transformer=None, tags=None):
        histogram = json_data[metric_name]

        for key, value in histogram.items():
            if key == "Time":
                value = nsToMs(value)
            if key_transformer:
                key = key_transformer(key)

            self.emitter.emit("%s%s%sHistogram.%s" % (prefix, alt_name if alt_name is not None else upperSnakeToCamel(metric_name), suffix, key), value, 'gauge', tags)

    def process_metric(self, json_data, metric_name, type, prefix="", alt_name=None, base_tags=dict(), parse_tags=dict(), transformer=None):
        try:
            for tags, value in self._extract_values(json_data, metric_name, parse_tags):
                all_tags = base_tags.copy() if base_tags else dict()
                all_tags.update(tags)
                if transformer:
                    value = transformer(value)
                self.emitter.emit("%s%s" % (prefix, alt_name if alt_name else metric_name), value, type, None if not len(all_tags) else all_tags)
        except KeyError, e:
            print "[KeyError] process_metric: Failed to get metric_name '%v' from json data. Skipping." % metric_name

    def _extract_values(self, json_data, metric_name, parse_tags):
        if parse_tags:
            return extract_tagged_values(json_data, metric_name, tag_list=parse_tags)
        return default_extractor(json_data, metric_name)

# For running locally, creates some mocks of collectd and allows passing arguments from the command line
def run_local(name, collector):
    import argparse, sys
    parser = argparse.ArgumentParser()
    parser.add_argument('--host', action='store',
                        help='Host to get JSON from', default="localhost")
    parser.add_argument('--port', action='store',
                        help='Port on host to get JSON from', default="15101")
    parser.add_argument('--host-path', action='store',
                        help='Path on host to get JSON from', default="/debug/vars")
    parser.add_argument('--file-path', action='store',
                        help='Local file to get JSON from')
    parser.add_argument('--interval', action='store',
                        help='How often (seconds) to output values', default=10)
    parser.add_argument('--verbose', '-v', action='store_true',
                        help='Whether to run in verbose mode')

    args = parser.parse_args()
    if args.file_path:
        json_provider = FileJsonProvider(args.file_path)
    else:
        json_provider = UrlJsonProvider(host=args.host, port=args.port, path=args.host_path)

    collectd = mock.CollectdMock(name)
    handler = CollectdLogHandler(collectd, '%s-mock' % name, verbose=args.verbose)
    handler.register()

    vt = collector(collectd, json_provider, args.verbose)
    interval = int(args.interval)
    while True:
        vt.read_callback()
        if interval == 0:
            sys.exit(0)
        else:
            time.sleep(interval)
