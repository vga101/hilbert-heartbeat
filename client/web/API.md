<a name="Heartbeat"></a>

## Heartbeat
This class provides functionality to send regular heartbeat
           signals to a HTTP server. Once initialized, there is usually
           no need to take further action except for changing the
           interval between subsequent heartbeats, see [setInterval](#Heartbeat+setInterval).
           Nevertheless, you can also disable automatic sending of heartbeat
           pings and send various heartbeat commands yourself.

**Kind**: global class  
**Access**: public  

* [Heartbeat](#Heartbeat)
    * [new Heartbeat(options)](#new_Heartbeat_new)
    * _instance_
        * [.send(command, interval, callback)](#Heartbeat+send) ⇒ <code>XMLHttpRequest</code>
        * [.sendSync(command, interval)](#Heartbeat+sendSync) ⇒ <code>String</code>
        * [.sendInit()](#Heartbeat+sendInit)
        * [.sendPing()](#Heartbeat+sendPing)
        * [.sendDone()](#Heartbeat+sendDone)
        * [.getInterval()](#Heartbeat+getInterval) ⇒ <code>Number</code>
        * [.setInterval(newInterval)](#Heartbeat+setInterval)
        * [.abort()](#Heartbeat+abort)
        * [.getUrl()](#Heartbeat+getUrl) ⇒ <code>Number</code>
        * [.getAppId()](#Heartbeat+getAppId) ⇒ <code>String</code>
        * [.getDebugLog()](#Heartbeat+getDebugLog) ⇒ [<code>debugLog</code>](#Heartbeat..debugLog)
        * [.setDebugLog(debugLog)](#Heartbeat+setDebugLog)
    * _static_
        * [.getInitCommand()](#Heartbeat.getInitCommand) ⇒ <code>String</code>
        * [.getPingCommand()](#Heartbeat.getPingCommand) ⇒ <code>String</code>
        * [.getDoneCommand()](#Heartbeat.getDoneCommand) ⇒ <code>String</code>
        * [.getPassedUrl([fallbackUrl])](#Heartbeat.getPassedUrl) ⇒ <code>String</code>
        * [.getPassedAppId([fallbackAppId])](#Heartbeat.getPassedAppId) ⇒ <code>String</code>
    * _inner_
        * [~debugLog](#Heartbeat..debugLog) : <code>function</code>
        * [~sendCallback](#Heartbeat..sendCallback) : <code>function</code>

<a name="new_Heartbeat_new"></a>

### new Heartbeat(options)
Creates an instance of the Heartbeat class.


| Param | Type | Default | Description |
| --- | --- | --- | --- |
| options | <code>Object</code> |  | JSON object containing initial heartbeat settings. |
| [option.url] | <code>String</code> |  | The base URL to use when sending the heartbeat. |
| [option.appId] | <code>String</code> |  | The application id that is send with each heartbeat. |
| [option.interval] | <code>Number</code> | <code>1000</code> | The interval between two heartbeat pings in milliseconds. Values <= 0 will disable automatic heartbeat pings. |
| [option.sendInitCommand] | <code>Boolean</code> | <code>false</code> | If the heartbeat init command should be send. If true, it will be send on the [window.onload](window.onload) event or immediately if [window.onload](window.onload) has already been triggered. |
| [option.sendDoneCommand] | <code>Boolean</code> | <code>false</code> | If the heartbeat done command should be send. If true, it will be send on the [window.onunload](window.onunload) event. |
| [option.debugLog] | [<code>debugLog</code>](#Heartbeat..debugLog) | <code>function(msg) {}</code> | Callback function for debug messages. |

**Example**  
```js
// Init and use internal defaults.
var heartbeat = new Heartbeat({});
```
**Example**  
```js
// Init and properly set base URL and application id with partial fallback.
var heartbeat = new Heartbeat({
    url: Heartbeat.getPassedUrl(),
    appId: Heartbeat.getPassedAppId('test_app')
});
```
**Example**  
```js
// Full initialization.
var heartbeat = new Heartbeat({
    url: Heartbeat.getPassedUrl('//localhost:8881'),
    appId: Heartbeat.getPassedAppId('test_app'),
    interval: 5000,
    sendInitCommand: true,
    sendDoneCommand: true,
    debugLog: function(msg) {
        console.log(msg);
    }
});
```
<a name="Heartbeat+send"></a>

### heartbeat.send(command, interval, callback) ⇒ <code>XMLHttpRequest</code>
Generic method for sending heartbeat commands to a heartbeat server.
The request will be send asynchronous, i.e. the method will return
almost immediately, but the callback will be called a some point in
the future.

**Kind**: instance method of [<code>Heartbeat</code>](#Heartbeat)  
**Access**: public  

| Param | Type | Description |
| --- | --- | --- |
| command | <code>String</code> | The heartbeat command to be send. |
| interval | <code>Number</code> | The interval in ms the heartbeat server has                            to expect between this and the next heartbeat                            command. |
| callback | [<code>sendCallback</code>](#Heartbeat..sendCallback) | Function to be called upon                                            success or failure. |

<a name="Heartbeat+sendSync"></a>

### heartbeat.sendSync(command, interval) ⇒ <code>String</code>
Generic method for sending heartbeat commands to a heartbeat server.
The request will be send synchronous, i.e. the method will block
until the request is finished.

**Kind**: instance method of [<code>Heartbeat</code>](#Heartbeat)  
**Returns**: <code>String</code> - - The response of the heartbeat server.  
**Throws**:

- <code>Error</code> - In case the request didn't succeed.

**Access**: public  

| Param | Type | Description |
| --- | --- | --- |
| command | <code>String</code> | The heartbeat command to be send. |
| interval | <code>Number</code> | The interval in ms the heartbeat server has                            to expect between this and the next heartbeat                            command. |

<a name="Heartbeat+sendInit"></a>

### heartbeat.sendInit()
Sends the init command asynchronously using default paramters and
without error handling or feedback.

**Kind**: instance method of [<code>Heartbeat</code>](#Heartbeat)  
<a name="Heartbeat+sendPing"></a>

### heartbeat.sendPing()
Sends the ping command asynchronously using default paramters and
without error handling or feedback.

**Kind**: instance method of [<code>Heartbeat</code>](#Heartbeat)  
<a name="Heartbeat+sendDone"></a>

### heartbeat.sendDone()
Sends the done command synchronously using default appId, 0ms interval
and without error handling or feedback. No further heartbeats will be
send after this command unless setInterval() is called again.

**Kind**: instance method of [<code>Heartbeat</code>](#Heartbeat)  
<a name="Heartbeat+getInterval"></a>

### heartbeat.getInterval() ⇒ <code>Number</code>
Get the current interval between two heartbeat pings in milliseconds.

**Kind**: instance method of [<code>Heartbeat</code>](#Heartbeat)  
**Access**: public  
<a name="Heartbeat+setInterval"></a>

### heartbeat.setInterval(newInterval)
Change the interval between two heartbeat pings.
This function sends out a heartbeat ping immediately to satisfy the
promise of the previous heartbeat. The next heartbeat will then be send
out after the specified number of milliseconds. If an interval <= 0 is
supplied, all pending heartbeats will be aborted and automatic sending of
heartbeats will be stopped.

**Kind**: instance method of [<code>Heartbeat</code>](#Heartbeat)  
**Access**: public  

| Param | Type | Description |
| --- | --- | --- |
| newInterval | <code>Number</code> | Interval between future heartbeat pings.                               Values <= 0 disable automatic heartbeat pings. |

<a name="Heartbeat+abort"></a>

### heartbeat.abort()
Abort all currently pending heartbeats, if any.

**Kind**: instance method of [<code>Heartbeat</code>](#Heartbeat)  
<a name="Heartbeat+getUrl"></a>

### heartbeat.getUrl() ⇒ <code>Number</code>
Get the base URL that is used for each heartbeat command.

**Kind**: instance method of [<code>Heartbeat</code>](#Heartbeat)  
**Access**: public  
<a name="Heartbeat+getAppId"></a>

### heartbeat.getAppId() ⇒ <code>String</code>
Get the application identifier that is send with each heartbeat command.

**Kind**: instance method of [<code>Heartbeat</code>](#Heartbeat)  
**Access**: public  
<a name="Heartbeat+getDebugLog"></a>

### heartbeat.getDebugLog() ⇒ [<code>debugLog</code>](#Heartbeat..debugLog)
Get the function that is used for debug logging.

**Kind**: instance method of [<code>Heartbeat</code>](#Heartbeat)  
**Access**: public  
<a name="Heartbeat+setDebugLog"></a>

### heartbeat.setDebugLog(debugLog)
Set the function that is used for debug logging.

**Kind**: instance method of [<code>Heartbeat</code>](#Heartbeat)  
**Access**: public  

| Param | Type |
| --- | --- |
| debugLog | [<code>debugLog</code>](#Heartbeat..debugLog) | 

<a name="Heartbeat.getInitCommand"></a>

### Heartbeat.getInitCommand() ⇒ <code>String</code>
Get the name of the 'init' command.

**Kind**: static method of [<code>Heartbeat</code>](#Heartbeat)  
**Access**: public  
<a name="Heartbeat.getPingCommand"></a>

### Heartbeat.getPingCommand() ⇒ <code>String</code>
Get the name of the 'ping' command.

**Kind**: static method of [<code>Heartbeat</code>](#Heartbeat)  
**Access**: public  
<a name="Heartbeat.getDoneCommand"></a>

### Heartbeat.getDoneCommand() ⇒ <code>String</code>
Get the name of the 'done' command.

**Kind**: static method of [<code>Heartbeat</code>](#Heartbeat)  
**Access**: public  
<a name="Heartbeat.getPassedUrl"></a>

### Heartbeat.getPassedUrl([fallbackUrl]) ⇒ <code>String</code>
Get the base URL that is passed as URL parameter HB_URL to this site.
If HB_URL is not set, [fallbackUrl](fallbackUrl) is used. If [fallbackUrl](fallbackUrl)
is not provided, an internal default will be returned.

**Kind**: static method of [<code>Heartbeat</code>](#Heartbeat)  
**Access**: public  

| Param | Type | Description |
| --- | --- | --- |
| [fallbackUrl] | <code>String</code> | Fallback that is used if HB_URL is not set. |

<a name="Heartbeat.getPassedAppId"></a>

### Heartbeat.getPassedAppId([fallbackAppId]) ⇒ <code>String</code>
Get the application id that is passed as URL parameter HB_APP_ID to this site.
If HB_APP_ID is not set, [fallbackAppId](fallbackAppId) is used. If [fallbackAppId](fallbackAppId)
is not provided, an internal default will be returned.

**Kind**: static method of [<code>Heartbeat</code>](#Heartbeat)  
**Access**: public  

| Param | Type | Description |
| --- | --- | --- |
| [fallbackAppId] | <code>String</code> | Fallback that is used if HB_APP_ID is not set. |

<a name="Heartbeat..debugLog"></a>

### Heartbeat~debugLog : <code>function</code>
This callback is used to log debug messages.

**Kind**: inner typedef of [<code>Heartbeat</code>](#Heartbeat)  

| Param | Type |
| --- | --- |
| message | <code>String</code> | 

<a name="Heartbeat..sendCallback"></a>

### Heartbeat~sendCallback : <code>function</code>
A callback for the asynchronous send method.

**Kind**: inner typedef of [<code>Heartbeat</code>](#Heartbeat)  

| Param | Type | Description |
| --- | --- | --- |
| error | <code>Error</code> | null in case of success, and Error object otherwise. |
| responseMessage | <code>String</code> | The response of the heartbeat server. |

