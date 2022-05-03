# Thread Monitoring tools

Javacores, and thread stacks in particular, are key debugging tools. Comparing stacks across threads, and for different points in time, can help narrow down the cause of performance slowdowns.

The challenge with Javacores/Threaddumps has always been associated to timing. Dumps needs to be collected at the exact time when the server is struggling. Some events are sporadic and short in duration, which makes the collection difficult. Often, by the time a problem is detected and a manual dump is collected, the problem has passed.

## Automatic thread dump collection

The *ThreadMonitor* tool automates thread dump collection. It offers options for the format, frequency and triggering of dumps. It integrates with the *Metrics* framework to enable automatic dump generation when certain thresholds, such as number of threads in use, are reached. With this configuration, the *ThreadMonitor* can automatically trigger the collection of dumps during spikes or slowdowns.

> The trigger based on number of threads in use requires metrics to be enabled in [values.yaml](https://github.com/HCL-TECH-SOFTWARE/hcl-commerce-helmchart/blob/87e05746dc4e5b412c663c858d180edcf2723e12/hcl-commerce-helmchart/stable/hcl-commerce/values.yaml#L363).

The ThreadMonitor tool is configured with the following YAML file which is available on Transaction Server, QueryApp, Solr Search and CRS containers. 
The configurations include format (i.e. Threaddump or Javacore), archiving, and threshold triggers.

For details of each configuration option, see the YAML file:

```
/SETUP/support/thread_monitor.yaml
```

The *ThreadMonitor* is enabled by default since HCL Commerce 9.1.9. 

It is configured to collect dumps in "threaddump" format (an HCL custom format), when the number of threads in use in the Default Executor/WebContainer pool exceeds a threshold value of 20. It will collect a maximum of 10 dumps per hour. These configurations can be updated to better match the scenario you are debugging.

> Changes to the configuration in *thread_monitor.yaml* are automatically loaded at runtime. A container restart is not required.

When a dump is collected due to the `webContainer.inUseLargerThan` threshold trigger, the following warning will be printed to the logs:
```
[4/12/22 16:20:43:937 GMT] 00000124 WebContainerI W com.hcl.commerce.monitor.thread.triggers.WebContainerInUseTrigger evaluateWebContainerUsage( final int inUse ) WebContainer threads in use 21 is higher than threshold of 20. Generating threaddump...
```

The *ThreadMonitor* can also be enabled and disabled from *Vault* by configuring the environment variable as follows: 
```
${TENANT}/${ENVIRONMENT}/${ENVTYPE}/threadMonitorEnable/${component_name}: value=true
```

## ThreadAnalyzer utility

The *ThreadMonitor* tool generates Javacores or Threaddumps in the directory specified by the *DUMP_DIR* environment variable. The *ThreadAnalyzer* utility can be used to facilitate the analysis. This is particularly helpful when dozens or hundreds of dumps are created--manual review can be time consuming.

The tool is available on the containers that enable the *ThreadMonitor*. It's found on this path:

```
/SETUP/support/thread-analyzer.jar
```

The usage is as follows:

```
java -jar thread-analyzer.jar
Use -y when running inside a container
usage: java -jar thread-analyzer.jar [options]
 -c,--config <arg>      Optional path to a Yaml configuration file
 -d,--directory <arg>   Directory or file where the dumps are found. If a
                        file is specified, only that dump is analyzed. If
                        the file is a Zip, all the dumps within the zips
                        are parsed. If the location is a directory, all
                        dumps and zips within the directory will be parsed
                        (this does not include subfolders). When not set,
                        the tool attempts to determine the directory to
                        use automatically. If a directory is not
                        discovered, it defaults to the current directory.
 -f,--follow            If enabled, the tool will continue to monitor for
                        new threaddumps.  This option is ignored if the
                        parameter is a file, not a directory. When -f is
                        set, -t is ignored.
 -h,--help              Prints this help.
 -r,--report <arg>      Comma separated list of reports. Defaults to 'Base
                        Web Activity'.
 -s,--since <arg>       Optional flag to limit the number of threadumps
                        Defaults to 3 hours. See 'time format'.
 -t,--to <arg>          Optional flag to limit the number of threadumps.
                        Defaults to now. See 'time format'.
 -x,--extract-config    Prints default config in stdout. This option is
                        used to customize the config, that can be then
                        specified with the -c option.
 -y,--yes               Required to acknowledge the utility can have an
                        impact when used within the container.

Time format: N[s=seconds, m=minutes, h=hours, d=days] OR yyyy-MM-dd HH:mm
OR epoch (e.g. 1650375222829) OR yyyyMMdd.HHmm[ss]

Available reports:
- Top Web Frames (tw): Reports the stacks most frequently found in threads
- Base Web Activity (ba): Summary of total base activities
- Web Activity (wa): Lists the discovered activity for each tread
```

> WARNING: When executed within the container, this utility takes CPU and memory resources. The amount will vary depending on the number of dumps processed. 
> For production environments, it is recommended to use this utility outside the container. Using -Xmx to limit memory usage is also highly recommended.

## ThreadAnalyzer activity logic

The *ThreadAnalyzer* tool generates reports such as *Base Web Activity (ba)* and *Web Activity (wa)* that rely on logic to "discover" key activites from a stack.
The configuration is generally based on applying RegEx patterns to stack frames, and to look for certain known classes and methods.

The following example, attaches the `DB2` activity to a stack with frames that include the package `com.ibm.db2.jcc`:

```
  - activity: DB2
    startsWith: com.ibm.db2.jcc
    consumePrevious: true
```

The out of the box configuration can be reviewed and extended.

- Use the `-x` argument to print the out-of-the-box configuration to the screen. The YAML output can be redirected to a file for editing:
```
java -jar thread-analyzer.jar  -x -y
```
- The customized configuration can be applied using the `-c` argument:
```
java -jar thread-analyzer.jar -c custom_config.yaml
```

### ThreadAnalyzer reports

#### Base Web Activity (ba) report

The *Base Web Activity (ba)* report summarizes activity for each Threaddump or Javacore. It includes the time of the dump, the file name, the total number of non-idle threads, and the base activities found. This report is useful to get a high level perspective of the problem areas and to narrow down the problem times, which typically show the most busy threads.

```
2021/10/26 13:10:12 - threaddump.20211026.131012.2913.0007.txt:   3 - SocketRead[DB2]:3
2021/10/26 13:10:42 - threaddump.20211026.131042.2913.0009.txt:  10 - SocketRead[DB2]:10
2021/10/26 13:11:12 - threaddump.20211026.131112.2913.0011.txt:  12 - SocketRead[DB2]:7 CMD(RetrieveCatalogEntryTask):3 DB2[DBQuery]:1 CMD(CheckCatalogEntryEntitlementBySearch):1
2021/10/26 13:11:27 - threaddump.20211026.131127.2913.0012.txt:  15 - CMD(RetrieveCatalogEntryTask):5 CMD(RetrieveContentTask):4 Web:4 CMD(InsertMoreMarketingContentAttachmentReferenceData):2
2021/10/26 13:11:42 - threaddump.20211026.131142.2913.0013.txt:   5 - Web:2 Commit:1 CMD(RetrieveContentTask):1 SocketRead[DB2]:1
2021/10/26 13:12:12 - threaddump.20211026.131212.2913.0015.txt:   2 - DB2[DBQuery]:3
2021/10/26 13:13:27 - threaddump.20211026.131327.2913.0020.txt:   2 - Web:1 SocketRead[DB2]:1
2021/10/26 13:13:42 - threaddump.20211026.131342.2913.0021.txt:   1 - SocketRead[DB2]:1
2021/10/26 13:14:12 - threaddump.20211026.131412.2913.0023.txt:   1 - CMD(RetrieveCatalogEntryTask):1
```

#### Web Activity (wa) report

The *Web Activity (wa)* report shows details at the thread level for each dump found, including the thread state and its activities.

```
2021/10/26 13:11:12 - threaddump.20211026.131112.2913.0011.txt:
   WebContainer : 0             RUNNABLE   [SocketRead[DB2], DBUpdate, Web]
   WebContainer : 3             RUNNABLE   [SocketRead[DB2], DBUpdate, Web]
   WebContainer : 9             RUNNABLE   [CMD(RetrieveCatalogEntryTask), CMD(FilterCatalogEntryTask), Web]
   WebContainer : 10            RUNNABLE   [SocketRead[DB2], DBUpdate, Web]
   WebContainer : 11            RUNNABLE   [SocketRead[DB2], DBQuery, CMD(RetrieveContentTask), CMD(FilterContentTask), Web]
   WebContainer : 13            RUNNABLE   [SocketRead[DB2], DBUpdate, Web]
   WebContainer : 16            RUNNABLE   [CMD(RetrieveCatalogEntryTask), CMD(FilterCatalogEntryTask), Web]
   WebContainer : 18            RUNNABLE   [DB2[DBQuery], CMD(RetrieveContentTask), CMD(FilterContentTask), Web]
   WebContainer : 19            RUNNABLE   [CMD(RetrieveCatalogEntryTask), CMD(FilterCatalogEntryTask), Web]
   WebContainer : 20            RUNNABLE   [SocketRead[DB2], DBQuery, CMD(RetrieveContentTask), CMD(FilterContentTask), Web]
   WebContainer : 21            RUNNABLE   [SocketRead[DB2], DBQuery, CMD(RetrieveCatalogEntryTask), CMD(FilterCatalogEntryTask), Web]
   WebContainer : 22            RUNNABLE   [CMD(CheckCatalogEntryEntitlementBySearch), CMD(CatalogFilterGetContractUnitPrice), CMD(ComposePriceForCatalogEntry), CMD(RetrieveCatalogEntryTask), CMD(FilterCatalogEntryTask), Web]
```

#### Top Web Frames (tw) report

The *Top Web Frames (tw)* report lists the most frequent stack frames for all the dumps found.

```
87 threaddumps, 98 total threads analyzed
       278 (284%) com.ibm.websphere.command.CacheableCommandImpl.execute(CacheableCommandImpl.java:167)
       244 (249%) com.ibm.commerce.command.MeasuredCacheableCommandImpl.execute(MeasuredCacheableCommandImpl.java:69)
       228 (233%) sun.reflect.DelegatingMethodAccessorImpl.invoke(DelegatingMethodAccessorImpl.java:55)
       128 (131%) com.ibm.commerce.foundation.client.facade.bod.AbstractBusinessObjectDocumentFacadeClient.internalSendBusinessObjectDocument(AbstractBusinessObjectDocumentFacadeClient.java:818)
       128 (131%) com.ibm.commerce.foundation.internal.client.services.invocation.InvocationService.invoke(InvocationService.java:113)
       128 (131%) com.ibm.commerce.foundation.internal.client.services.invocation.impl.NoInterfaceEJBInvocationBindingImpl.invoke(NoInterfaceEJBInvocationBindingImpl.java:225)
       128 (131%) com.ibm.commerce.foundation.client.facade.bod.AbstractBusinessObjectDocumentFacadeClient.sendBusinessObjectDocument(AbstractBusinessObjectDocumentFacadeClient.java:529)
       125 (128%) com.ibm.commerce.foundation.server.command.bod.BusinessObjectCommandTargetImpl.executeCommand(BusinessObjectCommandTargetImpl.java:116)
       125 (128%) com.ibm.commerce.foundation.server.command.bod.BusinessObjectDocumentProcessor.processBusinessObjectDocument(BusinessObjectDocumentProcessor.java:276)
       117 (119%) com.ibm.commerce.foundation.internal.server.command.impl.CommandTarget.executeCommand(CommandTarget.java:65)
       109 (111%) com.ibm.commerce.foundation.server.command.bod.AbstractGetBusinessObjectDocumentCmdImpl.performExecute(AbstractGetBusinessObjectDocumentCmdImpl.java:158)
        96 (98%) com.ibm.commerce.marketing.commands.marketingspot.MarketingSpotCommandBaseTaskCmdImpl.execute(MarketingSpotCommandBaseTaskCmdImpl.java:387)
```

> Percentages in excess of 100% mean the stack was found multiple times on a single thread

The report allows for configurations (using --extract-config and --config) as follows:

```
report:
  ...
  topWebFrames:
    minPercentage: 5
    excluded:
    - com.ibm.ws.
    - org.springframework.
    - javax.
    - java.
    - org.apache.wink.
    - com.ibm.io.
```

