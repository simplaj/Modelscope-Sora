import os
import json
from tqdm import tqdm

# 读取统计数据和原始数据
with open('../output/processed_data/duration_data_stats.jsonl', 'r') as sf:
    slines = sf.readlines()
    
with open('../output/processed_data/duration_data.jsonl', 'r') as df:
    dlines = df.readlines()
    
# 处理数据并保存结果
with open('../output/processed_data/duration_pro_data.jsonl', 'w') as out_file:
    for s, d in tqdm(zip(slines, dlines), total=min(len(slines), len(dlines))):
        stats = json.loads(s)
        content = json.loads(d)
        durations = stats.get('__dj__stats__', {}).get('video_duration', [])
        
        sub = 0
        videos_to_remove = []

        # 找到需要移除的视频索引
        for i, duration in enumerate(durations):
            if duration < 3 or duration > 10:
                videos_to_remove.append(i)
                sub += 1
        
        # 移除不符合时长的视频
        for index in sorted(videos_to_remove, reverse=True):
            content['videos'].pop(index)
            content['__dj__source_file__'].pop(index)
        
        # 更新文本中的占位符
        sourc = '<__dj__video>' * len(durations)
        tar = '<__dj__video>' * (len(durations) - sub)
        content['text'] = content['text'].replace(sourc, tar)
        
        out_file.write(json.dumps(content) + '\n')
