# collectd-vitess
A python Vitess plugin for CollectD.

It pulls `/debug/vars` data from vitess binaries (mainly vttablet and vtgate) to pull certain important and recommended
metrics.

## Installation
1. Place util.py and vtgate_collectd.py OR vttablet_collectd.py (depending on which metrics you are collecting) in your CollectD python plugins directory
2. Configure the plugin in CollectD
3. Restart CollectD

## Configuration
If you don’t already have the Python module loaded, you need to configure it first:

    <LoadPlugin python>
    	Globals true
    </LoadPlugin>
    <Plugin python>
    	ModulePath "/path/to/python/modules"
    </Plugin>

You should then configure the MySQL plugin:

	<Plugin "python">
    ModulePath "/usr/share/collectd/python/"

    Import "vtgate"

    <Module "vtgate">
      Verbose false
      Host "localhost"
      Port "15001"
    </Module>
  </Plugin>
  
## Metrics Collected

### VTTablet Metrics
      vitess.appConnPoolAvailable
      vitess.appConnPoolCapacity
      vitess.appConnPoolWaitCount
      vitess.appConnPoolAvgWaitTime
      vitess.connPoolAvailable
      vitess.connPoolCapacity
      vitess.connPoolWaitCount
      vitess.connPoolAvgWaitTime
      vitess.dbaConnPoolAvailable
      vitess.dbaConnPoolCapacity
      vitess.dbaConnPoolWaitCount
      vitess.dbaConnPoolAvgWaitTime
      vitess.streamConnPoolAvailable
      vitess.streamConnPoolCapacity
      vitess.streamConnPoolWaitCount
      vitess.streamConnPoolAvgWaitTime
      vitess.transactionPoolAvailable
      vitess.transactionPoolCapacity
      vitess.transactionPoolWaitCount
      vitess.transactionPoolAvgWaitTime
      vitess.errors
      vitess.healthcheckErrors
      vitess.infoErrors
      vitess.internalErrors
      vitess.kills
      vitess.mysql.totalCount
      vitess.mysql.count
      vitess.mysqlApp.totalCount
      vitess.mysqlApp.count
      vitess.mysqlDba.totalCount
      vitess.mysqlDba.count
      vitess.queries.totalCount
      vitess.queries.count
      vitess.transactions.totalCount
      vitess.transactions.count
      vitess.waits.totalCount
      vitess.waits.count
      vitess.queryCacheCapacity
      vitess.queryCacheLength
      vitess.queryCounts
      vitess.queryErrorCounts
      vitess.queryRowCounts
      vitess.queryAvgTime
      vitess.results.count
      vitess.streamlogDelivered
      vitess.streamlogDeliveryDroppedMessages
      vitess.streamlogSend
      vitess.tableACLAllowed
      vitess.tableACLDenied
      vitess.tableACLPseudoDenied
      vitess.tableACLExemptCount
      vitess.dataFree
      vitess.dataLength
      vitess.tableRows
      vitess.tabletState
      vitess.userTableQueryCount
      vitess.userTableQueryAvgTime
      vitess.userTransactionCount
      vitess.userTransactionAvgTime

### VTGate Metrics

      vitess.healthcheckConnections
      vitess.healthcheckErrors
      vitess.vtgateApiErrorCounts
      vitess.vtgateApiRowsReturned
      vitess.vtgateInfoErrorCounts
      vitess.vtgateInternalErrorCounts
      vitess.vttabletCallErrorCount
      vitess.vtgateApi.totalCount
      vitess.vtgateApi.latency
      vitess.vtgateApi.count
      vitess.vttabletCall.totalCount
      vitess.vttabletCall.count

## License
-------
The MIT License (MIT)

Copyright (c) 2016-2017 BetterCloud

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated
documentation files (the "Software"), to deal in the Software without restriction, including without limitation the
rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit
persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the
Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE
WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR
COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR
OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

