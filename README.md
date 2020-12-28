# 介绍

下载并合并高顿视频，魔改自jiangph1001的gaodun_download，增加了Windows支持


# 依赖

```
pip3 install pycryptodome
```

# 运行

按F12打开chrome的开发者模式，找到Network选项，然后刷新视频播放的页面，下面会出现一些记录

右键选择任意一条记录，找到`Save all as HAR with content`，保存到程序目录下的`HAR`文件夹中，例如此处命名为`test.har`

然后执行命令即可开始下载

```
python3 download.py
```



# 注意

- har目录下**不要放**不是har的文件
- 文件名必须以`.har`结尾
- 最后生成的视频文件名与har文件名和时间有关，例如
  - 保存的是`test.har`
  - 最后生成的视频文件是`test.ts`
- 可以往har文件夹中可以放入尽可能多的har文件，会依次下载
- 下载成功后，har文件会自动删除
- 已知bug：部分har文件cookie格式较为特殊，导致本脚本无法识别出key值，等待原作者更新算法