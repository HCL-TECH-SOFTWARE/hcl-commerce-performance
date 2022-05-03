# Troubleshooting Near-Real-Time (NRT) Index Building

Certain Management Center (CMC) operations, such as updating a product description, trigger a Near-Real-Time (NRT) delta build index with NiFi. Management Center uses HCL Cache [invalidation messages](Invalidations.md) to notify the NiFi server of the event. This document will help you troubleshoot the HCL Cache aspects of the NRT process.

## Troubleshooting Steps

### Confirm the Transaction Server is sending messages

When the Management Center operation is performed, the Transaction server will write the event on the *WCNifiDistributedMapCache* channel. Use the [SUBSCRIBE](https://redis.io/commands/subscribe) command to confirm the event is being written to the queue:

```
redis-cli subscribe "{cache-demoqaauth-services/cache/WCNifiDistributedMapCache}-invalidation"
```
> *The namespace will vary from system to system*

If the [SUBSCRIBE](https://redis.io/commands/subscribe) command does not capture any events, there might be a problem with the Redis connection from the Transaction server, or the specific event might not be configured to do so.

### Check if NiFi is listening on the Redis NRT queue

The NiFi server registers [PUBSUB](https://redis.io/docs/manual/pubsub/) listeners with Redis to receive the events.

Use the [PUBSUB CHANNELS](https://redis.io/commands/pubsub-channels/) command on all the master servers to confirm NiFi's listeners are enabled:

```
redis-cli pubsub channels | grep -i nifi
{cache-demoqaauth-services/cache/WCNifiDistributedMapCache}-invalidation
{cache-demoqaauth-services/cache/WCNifiBatchDistributedMapCache}-invalidation
```
If the listener (WCNifiDistributedMapCache) is not active, NiFi might not be running or might not be operating correctly.

### Use Tracing in NiFi to confirm listeners are active

The next step is to use tracing in NiFi to confirm the NRT listeners are triggering when events are posted to the channels (*WCNifiDistributedMapCache* and *WCNifiBatchDistributedMapCache*).

Enable the following traces in `logback.xml`:

```
<logger name="com.hcl.commerce.cache" level="TRACE" />
<logger name="org.redisson" level="TRACE" />
```

Confirm the listeners trigger by looking for the *onMessage* method in the trace:

```
... onMessage: onMessage(CharSequence pattern, CharSequence channel, String stringMessage) ..
```


