import torch
from PIL import Image
from transformers import AutoModel, AutoTokenizer
from decord import VideoReader, cpu
import json
import re
import sys
from tqdm import tqdm


MAX_NUM_FRAMES = 8

# 全局变量用于存储模型和tokenizer
global_model = None
global_tokenizer = None

def load_model_and_tokenizer():
    global global_model, global_tokenizer
    if global_model is None or global_tokenizer is None:
        global_model = AutoModel.from_pretrained('openbmb/MiniCPM-V-2_6', trust_remote_code=True,
                                                 attn_implementation='sdpa', torch_dtype=torch.bfloat16).eval()
        global_tokenizer = AutoTokenizer.from_pretrained('openbmb/MiniCPM-V-2_6', trust_remote_code=True)
    return global_model, global_tokenizer

def encode_video(video_path):
    def uniform_sample(l, n):
        gap = len(l) / n
        idxs = [int(i * gap + gap / 2) for i in range(n)]
        return [l[i] for i in idxs]

    vr = VideoReader(video_path, ctx=cpu(0))
    sample_fps = round(vr.get_avg_fps() / 1)
    frame_idx = [i for i in range(0, len(vr), sample_fps)]
    if len(frame_idx) > MAX_NUM_FRAMES:
        frame_idx = uniform_sample(frame_idx, MAX_NUM_FRAMES)
    frames = vr.get_batch(frame_idx).asnumpy()
    frames = [Image.fromarray(v.astype('uint8')) for v in frames]
    return frames

def generate_caption(video_path, gpu_id=0):
    torch.cuda.set_device(f'cuda:{gpu_id}')
    model, tokenizer = load_model_and_tokenizer()
    model = model.cuda()

    frames = encode_video(video_path)
    question = "Please directly describe the main objects in the video, including their colors, spatial relationships, and the overall scene. List all significant objects and explain their interactions. Describe it in a very very short sentence"

    msgs = [{'role': 'user', 'content': frames + [question]}]

    params = {
        "use_image_id": False,
        "max_slice_nums": 2
    }

    answer = model.chat(
        image=None,
        msgs=msgs,
        tokenizer=tokenizer,
        **params
    )
    return answer

def process_json_data(data, gpu_id=0):
    videos = data['videos']
    text = data['text']
    captions = []
    
    nums = text.count('<__dj__video>')

    for video_path in videos:
        caption = generate_caption(video_path, gpu_id)
        captions.append(caption)

    data['text'] = '<__dj__video>'*nums + ' '.join(captions).lower().replace('features', 'shows').replace('the video shows', '').replace('<|endoftext|>', '') + '<|__dj__eoc|>'
    return data

def read_jsonl(jsonl_path):
    datas = []
    with open(jsonl_path, 'r') as f:
        for line in f.readlines():
            data = json.loads(line)
            datas.append(data)
    return datas

if __name__ == '__main__':
    gpu_id = 0 if len(sys.argv) == 1 else sys.argv[1]
    gpu_id = int(gpu_id)

    # 输入 JSON 数据
    json_data_list = read_jsonl('/home/tzh/Project/dj_sora_challenge/output/processed_data/motion_data.jsonl')
    json_data_list = json_data_list[:len(json_data_list)//2] if gpu_id == 0 else json_data_list[len(json_data_list)//2:]

    # 加载模型和tokenizer
    load_model_and_tokenizer()

    # 处理每个 JSON 数据
    i = 0 # 计数器
    pro_data_cache = [] # 缓存处理后的数据
    with open(f'processed_data_{gpu_id}.json', 'a+') as f:
        for data in tqdm(json_data_list):
            processed_data = process_json_data(data, gpu_id=gpu_id)
            pro_data_cache.append(processed_data)
            i += 1
            if i == 1000:
                for s_cache in pro_data_cache:
                    f.write(json.dumps(s_cache) + '\n')
                i = 0 # 计数器归零
                pro_data_cache = [] # 清空缓存
        if pro_data_cache:
            f.write("\n".join([json.dumps(s_cache) for s_cache in pro_data_cache]) + "\n")

    print(f"Processing completed and results saved to 'processed_data_{gpu_id}.json'.")
