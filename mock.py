import sys

class CollectdMock(object):
  def __init__(self, plugin):
    self.value_mock = CollectdValuesMock
    self.notification_mock = CollectdNotificationMock
    self.plugin = plugin

  def info(self, msg):
    print 'INFO: %s' % (msg)

  def warning(self, msg):
    print 'WARN: %s' % (msg)

  def error(self, msg):
    print 'ERROR: %s' % (msg)
    sys.exit(1)

  def debug(self, msg):
    print 'DEBUG: %s' % (msg)

  def Values(self, plugin=None, plugin_instance=None, type=None, type_instance=None, values=None):
    return (self.value_mock)()

  def Notification(self, plugin=None, plugin_instance=None, type=None, type_instance=None, severity=None, message=None):
    return (self.notification_mock)()

class CollectdValuesMock(object):

  def dispatch(self):
        print self

  def __str__(self):
    attrs = []
    for name in dir(self):
      if not name.startswith('_') and name is not 'dispatch':
        attrs.append("%s=%s" % (name, getattr(self, name)))
    return "<CollectdValues %s>" % (' '.join(attrs))

class CollectdNotificationMock(object):

  def dispatch(self):
        print self

  def __str__(self):
    attrs = []
    for name in dir(self):
      if not name.startswith('_') and name is not 'dispatch':
        attrs.append("%s=%s" % (name, getattr(self, name)))
    return "<CollectdNotification %s>" % (' '.join(attrs))
