# Configuring PromotionArgument Database Records to Reduce Locking Conflicts

The promotion engine stores promotion execution details into the [PX_PROMOARG](https://help.hcltechsw.com/commerce/9.1.0/database/database/px_promoarg.html) database table. This table contains a `DETAILS` column with `CLOB` type. Under load, frequent updates to this table can impact database performance. 
Commerce includes a non-default configuration to avoid the use of the `DETAILS` column: see 
[Configuring PromotionArgument database records to reduce locking conflicts](https://help.hcltechsw.com/commerce/9.1.0/admin/tasks/tprconfigpromoargument.html).

This configuration requires both a database and a configuration update:

- Database update:
```
`INSERT INTO CMDREG (STOREENT_ID, INTERFACENAME, CLASSNAME) VALUES (0,'com.ibm.commerce.order.calculation.FinalizeDiscountCalculationUsageCmd', 'com.ibm.commerce.order.calculation.FinalizeDiscountCalculationUsageNoPromoargCmdImpl'); `
```
- Configuration update:
```
RUN sed -i 's/PromotionArgumentSessionBeanPersistenceManager/PromotionArgumentNoPromoargSessionBeanPersistenceManager/g' /opt/WebSphere/AppServer/profiles/default/installedApps/localhost/ts.ear/xml/PromotionEngineConfiguration/WCSPromotionEngineConfig.xml
```

