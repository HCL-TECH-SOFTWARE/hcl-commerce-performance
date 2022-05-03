# HCL Commerce - Using Redis with TLS

The HCL Cache can connect to Redis servers enabled with TLS. TLS is often required when using Redis as-a-service.

To indicate that the connection should be attempted with TLS, switch the protocol from `redis` to `rediss` as follows:

``` 
address: "rediss://127.0.0.1:6379"
```

The following settings are used to configure the connection:

*sslEnableEndpointIdentification*: Set to `true` to require the client to validate the Redis server's hostname using the server's certificate.
The Redis server's certificate must be present in the client's truststore. As this setting defaults to `true`, you must explicitely disable it when
endpoint identification is not possible or required.

*sslTruststore:* The location to the truststore file (.jks,.p12) that contains the Redis server public certificate. This is required
when `sslEnableEndpointIdentification` is set to `true`.

*sslTruststorePassword:* The password for the truststore.

## Truststore files used with HCL Commerce

Redis certificates are typically stored in the WebSphere Application Server default truststore. HCL Commerce provides a framework to automatically install certificates from Vault.
See  [Managing certificates with Vault](https://help.hcltechsw.com/commerce/9.1.0/install/refs/rigcertificates_vault.html) and  [Managing certificates manually](https://help.hcltechsw.com/commerce/9.1.0/install/refs/rigcertificates.html) for more details. Certificates can also be installed on  Java's default truststore.

[HCL Commerce 9.1.10+]
As the path to the WebSphere Application Server truststore can vary depending if running on WebSphere Liberty or Classic (ts-app), the HCL Cache provides the `${WEBSPHERE_TRUSTSTORE_PATH}`
variable that will automatically locate the truststore. When using `${WEBSPHERE_TRUSTSTORE_PATH}`, `sslTruststorePassword` does not need to be specified.

### Sample configuration

``` 
singleServerConfig:
  ...
  address: "rediss://hcl-commerce-redis-master.redis.svc.cluster.local:6379"
  sslEnableEndpointIdentification: true
  sslTruststore: "${WEBSPHERE_TRUSTSTORE_PATH}"
  ...
```


