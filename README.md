# Android 代理设置

[proxydroid](https://github.com/madeye/proxydroid) 是android上设置代理的一款软件，但是每次还是需要打开APP进行设置，部分时候不是特别方便。通过抽取里面的资源，做成一个电脑上可以执行的脚本工具，可以非常方便的设置app的代理。

设置代理

```shell
./setproxy.sh -p 192.168.1.211:8080 com.android.settings
```

取消代理

```shell
./setproxy.sh -u
```
