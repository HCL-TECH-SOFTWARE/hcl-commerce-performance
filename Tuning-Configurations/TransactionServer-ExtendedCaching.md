# Transaction Server - Extended Caching Configurations

## Transaction Server REST Caching for B2C

The Transaction Server container includes a sample `cachespec.xml` file that contains REST caching configurations for Emerald/B2C.
Implement the extended caching by merging the caching rules from `/opt/WebSphere/AppServer/profiles/default/installedApps/localhost/ts.ear/Rest.war/WEB-INF/cachespec.xml.emerald.sample.store` into the Rest.war `cachespec.xml` location: `/opt/WebSphere/AppServer/profiles/default/installedApps/localhost/ts.ear/Rest.war/WEB-INF/cachespec.xml`.

## Command Caching for Marketing

Enabling [Command caching for marketing](https://help.hcltechsw.com/commerce/9.1.0/admin/concepts/cdcmarcaccomcac.html) can improve performance and reduce the number of query executions.

To enable, merge the configurations in the sample file 
`/opt/WebSphere/AppServer/profiles/default/installedApps/localhost/ts.ear/Stores.war/WEB-INF/cachespec.xml.marketing` into the default cachespec.xml:
`/opt/WebSphere/AppServer/profiles/default/installedApps/localhost/ts.ear/Stores.war/WEB-INF/cachespec.xml`.
