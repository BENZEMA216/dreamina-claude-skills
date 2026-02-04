#!/bin/bash

LOGID="storyboard_act1_analysis_$(date +%s)"

curl --location "https://genai-sg-og.tiktok-row.org/gpt/openapi/online/v2/crawl?ak=${GEMINI3_API_KEY}" \
--header 'Content-Type: application/json' \
--header "X-TT-LOGID: $LOGID" \
--data '{
    "stream": false,
    "model": "gemini-3-pro-preview-new",
    "max_tokens": 4096,
    "messages": [
        {
            "role": "system",
            "content": "你是一位获奖的导演+摄影指导+分镜艺术家，拥有20年的行业经验。你精通视觉叙事、镜头语言、剪辑节奏和导演思维。"
        },
        {
            "role": "user",
            "content": "请专业分析《一个番茄的非自然死亡》第一幕（困局）的分镜脚本。\n\n【第一幕概要】\n- 总计31个镜头，预估4分钟\n- 5个场景：被吵醒→洗漱→早餐冲突→楼道宣泄→大院阳光\n- 核心角色：李蔚（18岁女主）、张明蔚（母亲）、李从安（父亲）\n\n【关键镜头分析】\n场景1(镜号1-1至1-5)：黑场淡入，厨房杂音，李蔚被吵醒看见发霉天花板\n场景3(镜号1-10至1-24)：番茄特写，李蔚伸手被母亲拍掉，家庭矛盾爆发\n场景4(镜号1-25至1-29)：楼道踢碎花瓶，情绪宣泄\n场景5(镜号1-30至1-31)：从阴暗楼道到阳光，主观视角看天空\n\n【分析要求】\n1. 空间构成：评估画面层次、视觉引导、场面调度\n2. 镜头设计：景别选择、运镜方式、焦距建议\n3. 叙事逻辑：时空连续性、情感递进、剪辑节奏\n4. 制作评估：拍摄难度、设备需求、预算考量\n5. 创意建议：可借鉴的经典案例、具体优化方案\n\n【重点关注】\n- 番茄作为核心意象的呈现力度\n- 母女关系的视觉语言表达\n- 压抑到释放的情绪曲线设计\n- 南方小城氛围的真实感营造\n\n请以专业导演视角提供批判性分析，指出问题并给出可执行的改进建议。"
        }
    ],
    "thinking": {
        "include_thoughts": true,
        "budget_tokens": 8192
    }
}'