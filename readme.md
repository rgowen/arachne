#arachne
==========

arachne is an IP ranger scanner written in Python. It currently is quite simple and only looks for positive HTTP responses, and returns those to a text file.

##Usage
==========
```
arachne.py -b [IP range begin] -e [IP range end]
```

Optional parameters:

```
-n Specify number of threads to use (default is 1)
```
```
-t Add page titles to output file
```
