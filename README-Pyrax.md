# About Pyrax

* To access Rackspace APIs, Pyrax-library is needed.
* There are alternative Python implementation for Rackspace API,
but you cannot use them for this.
* Bad news: Pyrax has a bug, that prevents it from working correctly on Python 3.x.
  * Details are at [parse.py string creation error #565](https://github.com/pycontribs/pyrax/issues/565)
* Good news: You can navigate around the problem.

## Pyrax has been obsoleted!
That's more bad news. Read all about that from https://github.com/pycontribs/pyrax.

## Pyrax does support Rackspace API v1
* Alternatives like RackspaceSDK-plugin will support *only* v2 (or newer) OpenStack-compatible APIs.
* Read about RackspaceSDK-plugin from https://github.com/rackerlabs/rackspace-sdk-plugin
* Read about Rackspace Cloud DNS API 1.0 from https://developer.rackspace.com/docs/cloud-dns/v1/

## Ultimately ...
There is no real alternative for using Pyrax.

## Patch
````
--- pyrax/resource.py-orig      2018-08-29 18:19:53.024094581 +0200
+++ pyrax/resource.py   2018-08-31 20:12:40.369778180 +0200
@@ -68,7 +68,9 @@
         corresponding attributes on the object.
         """
         for (key, val) in six.iteritems(info):
-            if isinstance(key, six.text_type):
+            # XXX
+            # https://github.com/jaraco/pyrax/commit/c72aff60924689d65384270f1c8309a7a65ef2ef
+            if isinstance(key, six.text_type) and six.PY2:
                 key = key.encode(pyrax.get_encoding())
             elif isinstance(key, bytes):
                 key = key.decode("utf-8")
````
