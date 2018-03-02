# JavaScript implementation of Hilbert's heartbeat protocol

This JavaScript library implements the heartbeat protocol defined in the [top-level `README.md`](../../README.md). The API documentation is located in [`API.md`](API.md).

The library has two basic operation modes: It can either send heartbeats automatically based on a fixed time interval or you can send them manually at appropriate locations in your code.

## Basic usage

Add
```HTML
<script src="hilbert-heartbeat.js"></script>
<script>
  var heartbeat = var heartbeat = new Heartbeat({
    url: Heartbeat.getPassedUrl(),
    appId: Heartbeat.getPassedAppId()
  });
</script>
```
to the `<head>` of your HTML document and open the page using a query string with appropriate values for `HB_APP_ID` and `HB_URL` like so:
```
your-page.html?HB_APP_ID=my_app&HB_URL=http://localhost:8888
```
That's all.

After `window.onLoad`, the `heartbeat` object will start sending one heartbeat ping per second for `my_app` to `http://localhost:8888`. No `hb_init` or `hb_done` command will be send. 

You can also supply parameters directly or provide a fallback value:
```JavaScript
var heartbeat = var heartbeat = new Heartbeat({
 url: Heartbeat.getPassedUrl('http://localhost:8080'), // will use the URL parameter if present,
                                                       // the fallback otherwise
 appId: 'another_app'                                  // provide the value directly
});
```
There are even more parameters that can be adjusted:
```JavaScript
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
In the above example, the heartbeat pings will be sent once every five seconds and `hb_init` and `hb_done` commands will be send as well.

Embedded into HTML, the above might look like this:
```HTML
<!DOCTYPE html>
<html>
    <head>
        <title>Testing HB library for JS: hilbert-heartbeat.js </title>
        <meta http-equiv="Content-Type" content="text/html; charset=utf-8" />
        <script src="hilbert-heartbeat.js"></script>
        <script>
            var heartbeat;
            window.onload = function() {
                var responsesDiv = document.getElementById("responses");
                heartbeat = new Heartbeat({
                    url: Heartbeat.getPassedUrl('http://localhost:8888'),
                    appId: Heartbeat.getPassedAppId('test_app'),
                    interval: 5000,
                    sendInitCommand: true,
                    sendDoneCommand: true,
                    debugLog: function(msg) { responsesDiv.innerHTML += msg + "<br />"; }
                });
            };
        </script>
    </head>
    <body>
        <h1>HB messages should follow : </h1><br /><hr />
        <div id="responses"></div>
    </body>
</html>
```

## Advanced usage
### Adjusting the interval
If you have a long running task in your application that is likely to block the event queue for a while, you can raise the heartbeat interval to the expected duration of the computation (or better a bit higher):
```
var previousInterval = heartbeat.getInterval();
heartbeat.setInterval(10000);
```
This immediately sends another heartbeat ping with adjusted expected duration until the next ping. The application now has ten seconds to do whatever it needs to do. Afterwards you can set it back to normal:
```
heartbeat.setInterval(previousInterval);
```
Usually, a long blocking JavaScript function has other bad side-effects and should be avoided if possible.

### Disabling automatic sending of heartbeats
You can also send heartbeats by hand by setting
```
heartbeat.setInterval(-1);
```
or even
```
var heartbeat = new Heartbeat({
  interval: -1
  // don't forget to set the other option you need
});
```
to disable it from the very beginning.

Afterwards, you can use the `sendPing()`, `sendInit()` and `sendDone()` commands:
```
// beginning of your program
heartbeat.sendInit();

// every once in a while during normal operation
heartbeat.sendPing();

// end of your program
heartbeat.sendDone();
```
Note that you still should not wait longer then `heartbeat.getInterval()` milliseconds until sending the next heartbeat.

### Full control over the heartbeat command
The `send()`, `sendSync()` and `sendBeacon()` methods give you full control over the heartbeat requests sent.

#### Asynchronous operation
Usually, heartbeats should be sent asynchronously:
```
var cb = function(err,response) {
  if(err)
    console.log("Error!");
  else
    console.log("Success: " + response);
};
var xhttp = heartbeat.send(Heartbeat.getPingCommand(),2000,cp);
```
In this example, `xhttp` is a `XMLHttpRequest` object whose `send()` method has already been called. It can be useful if you need to abort a certain request. You should send the next heartbeat within the next two seconds after the current one.

If you are not interested in the response of the heartbeat server, you should use `sendBeacon()` instead. It will only work with recent browser versions (because it relies on `navigator.sendBeacon()`), but if it is available, it will also work on an `unload` event, e.g. for sending the `hb_done` command (which might not be delivered on `unload` when `send()` or `sendSync()` are used).

#### Synchronous operation
Sometimes, doing a blocking call can be useful:
```
heartbeat.abort();
var response = heartbeat.sendSync(Heartbeat.getDoneCommand(),0);
```
The `abort()` command beforehand makes sure that no other asynchronous requests are in the pipeline before the `hb_done` command is send out. Otherwise, the heartbeat server might receive them out of order. Note that using `sendSync()` on an `unload` event might not work as expected. Use `sendBeacon()` instead.

## Generating the API documentation

The file [API.md](API.md) is generated by the [`jsdoc2md`](https://www.npmjs.com/package/jsdoc-to-markdown) tool based on the [JSDoc](https://usejsdoc.org) comments in the source code. You need Node.js installed to proceed.

### With `npx` (prefered)
[`npx`](https://www.npmjs.com/package/npx) allows to use tools provided via Node.js packages without installing them globally. So you only need `npx` globally and nothing else. It's also easier to lock tool versions.
```
npm install -g npx
npx --package jsdoc-to-markdown@4 jsdoc2md hilbert-heartbeat.js > API.md
```

### Without `npx`
You can also install `jsdoc2md` globally via
```
npm install -g jsdoc-to-markdown@4
```
at the expense of polluting your global namespace and then run
```
jsdoc2md hilbert-heartbeat.js > API.md
```
