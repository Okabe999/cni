<picture>
  <source media="(prefers-color-scheme: dark)" srcset="https://user-images.githubusercontent.com/25423296/163456776-7f95b81a-f1ed-45f7-b7ab-8fa810d529fa.png">
  <source media="(prefers-color-scheme: light)" srcset="https://user-images.githubusercontent.com/25423296/163456779-a8556205-d0a5-45e2-ac17-42d089e3c3f8.png">
  <img alt="Shows an illustrated sun in light mode and a moon with stars in dark mode." src="https://user-images.githubusercontent.com/25423296/163456779-a8556205-d0a5-45e2-ac17-42d089e3c3f8.png">
</picture>

# 操作指南

### 集群环境

1. 集群环境：ubuntu20.04 
2. k8s version：v1.23.0
3. go version：go1.21.0 linux/amd64
4. gcc version： 9.4.0

若有学习需求，需先安装k8s集群，安装k8s集群可以参考这篇文章https://zhuanlan.zhihu.com/p/654320979
需要准备至少两台主机，一台master、一台node。

在准备k8s环境的时候，若vim `/etc/docker/daemon.json`时阿里云的源不好用，可以使用[dockerpull.com](dockerpull.com)提供的方法。

### 运行步骤
**1.日志准备**  

使用Camflow系统捕获日志文件,在Ubuntu上安装Camflow系统可以参考此网址[camflow](https://camflow.org/#package)   
安装需要编译linux内核模块，可能比较耗时。  
另外确保当前文件夹内存在以规范命名的Camflow的日志log文件，例如44_577844575_276576.log。    

**2.代码运行**
git clone https://github.com/Okabe999/cni.git
运行代码需要准备如下文件：  
1.CamFlow系统捕获的log日志，命名规范为44_577844575_276576.log  
2.jsonpath.txt文件，该文件的内容应存放log日志文件的路径+名称，例如，若44_577844575_276576.log和jsonpath.txt在同一目录结构下，44_577844575_276576.log的文件路径便可省略，不然应保存完整绝对路径，例如/root/extra/44_577844575_276576.log  
3.在k8s环境下，假设存在master、node1、node2三台主机。
在master节点上的simple-k8s-cni目录下运行以下命令  
make docker-build  
make kind-image-load  
kubectl apply -f deploy/mycni.yaml  
在master节点上，使用scp命令将extra文件夹里的代码复制到在node1、node2节点上，例如scp XXX root@ding-net-node-1:/root
然后就可以测试apply pod了  
**3.测试pod**

以下是一段测试pod，文件名为busybox：  

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: busybox
spec:
  selector:
    matchLabels:
      app: busybox
  replicas: 3
  template:
    metadata:
      labels:
        app: busybox
    spec:
      containers:
      - name: busybox
        image: busybox
        command:
          - sleep
          - "36000"
        imagePullPolicy: IfNotPresent
```yaml
在master节点上使用kubectl apply -f ../simple-k8s-cni-1/busybox.yaml(此处为busybox.yaml的文件路径)，便可创建三个测试pod  
在master节点上kubectl apply成功之后，便可切换到node1、node2中，使用ls查看是否存在feature.csv文件

