# JDBC Monitor

The JDBC Monitor utility is available with the Transaction Server. It can log details of the JDBC queries executed for profiling and debugging. 

## Configuration

The JDBC Monitor configuration is a two step process. The Java agent must be enabled before the desired log level configuration can be used in runtime.

### Enabling the Java agent

The JDBC Monitor Java agent injects debugging code on the WebSphere JDBC access APIs. The agent does not add overhead unless tracing is enabled, but it is still
recommended that the agent is only enabled on environments where the JDBC Monitor is intended to be used.

To enable the JDBC Monitor Java agent, add the *JDBC_MONITOR_ENABLED* environment variable to the ts-app deployment:

```
  - env:
    - name: JDBC_MONITOR_ENABLED
      value: "true"
```

The same can also be done with Vault:

```
${VAULT_URL}/${TENANT}/${ENVIRONMENT}/${ENVTYPE}/jdbcMonitorEnable/ts-app
value: true
```

### Using Java loggers to print debugging information

Once the Java agent is enabled, the JDBCMonitor logging levels can be used to print query details as follows:

*com.hcl.commerce.monitor.jdbc.JDBCMonitor=level*
- *fine*: Query text and execution time
- *finer*: fine + parameter marker values
- *finest*: finer + java stack

To log during startup, use the *TRACE_SPEC*  environment variable:

```
  - env:
    - name: TRACE_SPEC
      value: com.hcl.commerce.monitor.jdbc.JDBCMonitor=fine
```

Or the corresponding Vault entry:

```
${VAULT_URL}/${TENANT}/${ENVIRONMENT}/${ENVTYPE}/traceSpecification/ts-app
```

In runtime, the *set-dynamic-trace-specification* run-engine command can be used:

```
run set-dynamic-trace-specification com.hcl.commerce.monitor.jdbc.JDBCMonitor=fine
<< reproduce the issue >> 
run set-dynamic-trace-specification *=info
```


##### Sample log entries:

*Fine:*

```
[7/8/21 16:06:13:860 GMT] 000000eb JDBCMonitor   1 com.ibm.ws.rsadapter.jdbc.WSJdbcPreparedStatement executeQuery "WSJdbcPreparedStatement executeQuery":{ "durationMs":0.77,"query":"SELECT T1.ORDIADJUST_ID, T1.ORDADJUST_ID, T1.ORDERITEMS_ID, T1.AMOUNT, T1.OPTCOUNTER FROM ORDIADJUST T1 WHERE (T1.ORDERITEMS_ID = ?)"}
```
*Finer:*

```
[7/8/21 16:07:21:488 GMT] 000000eb JDBCMonitor   2 com.ibm.ws.rsadapter.jdbc.WSJdbcPreparedStatement executeQuery "WSJdbcPreparedStatement executeQuery":{ "durationMs":0.63,"query":"select NAME,VALUE,TYPE from ORDITEMEXTATTR where ORDERITEMS_ID=? ","parameters":"{"1":"15007"}"}
```
*Finest:*

```
[7/8/21 16:09:00:360 GMT] 00000103 JDBCMonitor   3 com.ibm.ws.rsadapter.jdbc.WSJdbcPreparedStatement executeQuery "WSJdbcPreparedStatement executeQuery":{ "durationMs":1.18,"query":"select PX_RWDOPTION_ID, PX_PROMOTION_ID,ORDERS_ID, RWDCHOICE, RWDSPEC, OPTCOUNTER from PX_RWDOPTION where ORDERS_ID=? ORDER BY PX_RWDOPTION_ID","parameters":"{"1":"4023252"}","stack":"["java.lang.Thread.getStackTrace(Thread.java:1164)","com.ibm.ws.rsadapter.jdbc.WSJdbcPreparedStatement.executeQuery(WSJdbcPreparedStatement.java:778)","com.ibm.commerce.base.helpers.BaseJDBCHelper.executeQuery(BaseJDBCHelper.java:408)..."
```

## parse_logs.py - Python Log Parser Script 

The [parse_logs.py](parse_logs.py) Python script can facilitate analysis by extracting JDBC operations from the trace and creating a CSV report file.


>>>
  This parser reads trace files and for each, it generates 2 output files. The 1st one contains the queries with their response time,
  parameter values, and stack and the 2nd file is a grouping of the same queries with number of calls, percentiles and sum of resp. time.

  Usage
  -----
    python parse_logs.py
        -p <path_to_trace_files>    Path where to look for trace files. If not provided, it defaults to current folder.

        -f <trace_file(s)>          Trace file(s) to parse. One trace file or more separated by commas. Wildcards can also be used.

        -c                          Concatenate the queries with their parameter values. The default is not to concatenate

        -g                          Grouping the trace files. The default is to not group and generate 2 query files for each trace file.

        -k <keyword>                This keyword parameter is used to filter the queries. Only the ones that have this keyword(s)
                                    in their stack will be added to the csv/XL files. Can use multiple keywords separated by comma.

        -u < all | any >            Usage of the keyword. This parameter is used when multiple keywords are used.
                                    If all is used. A query is picked if all keywords are found in the stack.
                                    If any is used. A query is picked if any keyword is found in the stack.
                                    This parameter is considered only if -k and multiple keywords are used.

        -o <output_folder>          Output folder where to save the output files. If not provided, it defaults to current folder.

        -h                          Print this help.
>>>
