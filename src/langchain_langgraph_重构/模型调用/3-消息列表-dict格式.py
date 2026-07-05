"""
消息列表可采用dict格式，内部为多个角色的：{role-content}

这个格式更符合 openai api
"""

import os
from dotenv import load_dotenv
from langchain.chat_models import init_chat_model
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage

# 加载环境变量
load_dotenv()
DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY")
DEEPSEEK_BASE_URL = os.getenv("DEEPSEEK_BASE_URL")

# 校验 key 和 url
if not DEEPSEEK_API_KEY or DEEPSEEK_API_KEY == "your_api_key_here":
    raise ValueError("\n请先在 .env 文件中设置有效的 DEEPSEEK_API_KEY\n")

if not DEEPSEEK_BASE_URL or DEEPSEEK_BASE_URL == "your_base_url_here":
    raise ValueError("\n请先在 .env 文件中设置有效的 DEEPSEEK_BASE_URL\n")

# 初始化模型
model = init_chat_model(
    model="deepseek-v4-flash",
    model_provider="openai",
    api_key=DEEPSEEK_API_KEY,
    base_url=DEEPSEEK_BASE_URL,
    temperature=0.8,
)


# 使用dict格式的消息列表
def example_3_dict_message():
    messages = [
        {
            "role": "system",
            "content": "你是一名专业的高中数学教师，具有丰富的教学经验。",
        },
        {
            "role": "user", 
            "content": "高中教学包含哪几个重要部分？"
        },
    ]

    response = model.invoke(messages)

    print(f"\nAI回复：\n{response.content}")


# 主程序
def main():
    try:
        example_3_dict_message()
    except Exception as e:
        print(f"\n运行出错：{e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    main()

"""
AI回复：
作为一名有多年教学经验的高中数学教师，我认为高中教学（尤其以数学为例）的成功实施，主要包含以下几个核心部分：

1. **知识体系的构建（教学内容）**  
   这是教学的基础。高中数学的模块化很强，需要将代数、几何、概率统计、函数等知识按照课标和教材，由浅入深地编织成网络。重点不是孤立地讲公式，而是讲清知识的来龙去脉和内在联系，比如函数与方程、数与形的转化。

2. **思维能力的培养（教学核心）**  
   高中教学不能只停留在“会做题”，而要着力提升逻辑推理、抽象概括、运算求解、空间想象和数据分析这五大关键能力。例如，在讲圆锥曲线时，不仅要教学生如何联立方程，更要通过几何直观培养他们“用代数眼光看几何问题”的思维。

3. **教学法与课堂设计（教学过程）**  
   不同内容需要不同教法。新授课我会注重情境引入（比如用生活实例或数学史激发兴趣），习题课强调变式训练和一题多解，复习课则用思维导图帮助学生构建体系。课堂中要留出“生成性问题”的空间，鼓励学生质疑和讨论。

4. **评价与反馈机制（教学闭环）**  
   包括平时作业、单元测验、错题分析以及阶段性诊断。我会特别强调错题本的“二次加工”——不是简单抄题，而是分析错因、总结解法、对比同类题。同时通过课堂提问、小组互批等方式，让学生能清晰地知道自己的薄弱点在哪。

5. **分层教学与个性化辅导（学生差异）**  
   高中学生分化明显。对基础薄弱的学生，我会降低起点，先讲清课本原理、抓计算规范；对学有余力的学生，则补充竞赛思维或高考压轴题套路。例如，讲授导数时，对后进生重点要求“会用求导公式”，对尖子生则要求能证明“函数隐零点”的单调性。

6. **非智力因素的培育（学习动力）**  
   高中学习压力大，心态和习惯往往决定成败。我会在教学中渗透“延迟满足”的理念，帮助学生建立长期目标；通过展示数学之美（如三角函数的对称性、数列的规律性）激发内在兴趣。同时，针对考试焦虑、粗心等心理问题，也会在习题讲评中给出具体对策，比如“审题三步法”。

以上六个部分是一个有机的整体。比如，**知识体系是骨架，思维能力是灵魂，教学法是载体，评价是诊断，分层是关怀，非智力因素是能量**。好的教学就是让这些部分协同运转，让每个学生都能在自己原有的基础上获得可见的进步。
"""
