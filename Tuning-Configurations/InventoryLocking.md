# Inventory Locking with Frequently Updated Items

*This function is enabled by default since 9.1.11*

When the Non-ATP inventory model is used, database update locks are held on [INVENTORY](https://help.hcltechsw.com/commerce/9.1.0/database/database/inventory.html) table rows until the end of the OrderProcess transaction. The locks block other Orders for the same items from being processed concurrently.

A new `updateImmediately` configuration is introduced. INVENTORY Update locks are not obtained in the OrderProcess transaction. Instead, the INVENTORY rows are updated in a separate, much shorter transaction, and are committed as soon as possible. If the OrderProcess transaction is rolled back, then the INVENTORY updates are reversed, also in a separate transaction. Since the locks are held for a shorter time, this configuration can reduce response times when multiple shoppers buy the same item at the same time.

To configure this new behavior, add the following to the InstanceProperties tag in the `wc-server.xml` instance configuration file: 

```
<com.ibm.commerce.fulfillment.commands.InventoryUpdateHelper updateImmediately="true"/>
```
For example:

```
# Inventory Locking
RUN sed -i 's/<InstanceProperties>/<InstanceProperties>\n <com.ibm.commerce.fulfillment.commands.InventoryUpdateHelper updateImmediately="true" \/>/g' /opt/WebSphere/AppServer/profiles/default/installedApps/localhost/ts.ear/xml/config/wc-server.xml
```
