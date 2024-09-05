# Modelscope-Sora
Modelscope-Sora Challenge 第四名解决方案

```mermaid
flowchart LR
    A[开始] --> B[视频处理]
    B --> C[场景分割]
    C --> D[时长过滤]
    D --> E[时长进一步处理]
    E --> F[美学评分过滤]
    F --> G[运动评分过滤]
    G --> H[文本处理]
    
    H --> I[MiniCPM 生成 caption]
    I --> J[Unicode 修复]
    J --> K[结束]
    
    %% 使用 classDef 和 class 来定义和应用样式
    classDef processGroup fill:#f9f,stroke:#333,stroke-width:2px;
    class B,C,D,E,F,G processGroup;
    class H,I,J processGroup;
    
    %% 使用不可见节点强制分行
    G --> Z((()))
    Z --> H
    linkStyle 7 stroke:none;
    style Z height:0px,width:0px;
```

## 视频处理
### 1.1 场景分割
使用 PySceneDetect 的 ContentDetector 将视频拆分为场景剪辑。

### 1.2 时长过滤
保留视频时长在 3 到 10 秒之间的数据样本。

### 1.3 时长进一步处理
移除不符合时长要求的视频,并更新文本中的占位符。

### 1.4 美学评分过滤
根据从视频中提取的帧图像的美学评分过滤样本。

### 1.5 运动评分过滤
保留视频运动分数在特定范围内的样本。

## 文本处理
### 2.1 MiniCPM 生成 caption
使用 MiniCPM-V-2_6 模型为视频生成描述。

### 2.2 Unicode 修复
修复文本中的 Unicode 错误,删除重复的句子,并过滤单词重复比例超出特定范围的文本。
