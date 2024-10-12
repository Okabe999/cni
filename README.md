<picture>
  <source media="(prefers-color-scheme: dark)" srcset="https://user-images.githubusercontent.com/25423296/163456776-7f95b81a-f1ed-45f7-b7ab-8fa810d529fa.png">
  <source media="(prefers-color-scheme: light)" srcset="https://user-images.githubusercontent.com/25423296/163456779-a8556205-d0a5-45e2-ac17-42d089e3c3f8.png">
  <img alt="Shows an illustrated sun in light mode and a moon with stars in dark mode." src="https://user-images.githubusercontent.com/25423296/163456779-a8556205-d0a5-45e2-ac17-42d089e3c3f8.png">
</picture>

# 操作指南

### 集群环境

1. 集群环境：ubuntu20.04 虚拟机
2. k8s version：v1.23.0
3. go version：go1.21.0 linux/amd64
4. gcc version： 9.4.0

![Untitled](https://prod-files-secure.s3.us-west-2.amazonaws.com/ccaacad4-ec36-4d9a-9182-238ca30ae37e/1fb012c7-b4ae-4ffb-bb11-6c33d28a6710/Untitled.png)

安装k8s集群可以参考这篇文章https://zhuanlan.zhihu.com/p/654320979

vim `/etc/docker/daemon.json`若阿里云的源不好用，可以使用dockerpull.com提供的方法。
