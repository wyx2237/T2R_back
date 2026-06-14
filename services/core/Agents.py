"""
# 结构化计算路径生成的四阶段workflow
步骤分解 -> 流程定义 -> 依赖验证 -> 代码生成

"""
import sys
import asyncio
from autogen_agentchat.agents import AssistantAgent
from services.core.Models import deepseek_v4_pro_client, qwen3_8b_model_client
from services.core.Prompts import EXTRACT_PARAMETERS_PROMPT, QUESTION_DECOMPOSITION_PROMPT_ALL, WORKFLOW_MODELING_PROMPT, DEPENDENCY_VERIFICATION_PROMPT, CODE_GENERATION_PROMPT
from services.core.Prompts import QUESTION_DECOMPOSITION_WO_ATOMIC
MODEL_CLIENT = deepseek_v4_pro_client
# MODEL_CLIENT = qwen3_8b_model_client
"""
# Step1: 步骤分解
- 将需要计算的复杂问题拆分为多个简单独立的子步骤
- 如果已经是简单问题则不需要再拆分
- 步骤序列长度 <= 6 
"""
def get_QuestionDecomposer():
    QDPrompt = QUESTION_DECOMPOSITION_PROMPT_ALL
    # print("WITH_ATOMIC_PROMPT")
    return AssistantAgent(
        model_client=MODEL_CLIENT,
        name="QuestionDecomposer",
        description="一个能够将复杂问题拆分为若干简单步骤的问题分析智能体",
        system_message=QDPrompt,
        output_content_type_format="json"
    )

def get_QuestionDecomposer_wo_Atomic():
    Prompt = QUESTION_DECOMPOSITION_WO_ATOMIC
    print("WO_ATOMIC_PROMPT")
    return AssistantAgent(
        model_client=MODEL_CLIENT,
        name="QuestionDecomposer",
        description="一个能够将复杂问题拆分为若干简单步骤的问题分析智能体",
        system_message=Prompt + "\nNone",
        output_content_type_format="json"
    )
"""
# Step2: 流程定义
- 根据前面生成的步骤序列，定义计算流程JSON
- 所有步骤按照问题的执行逻辑排列
- 定义原始输入字典和最终输出变量
"""

def get_WorkflowModeler():
    WMPrompt = WORKFLOW_MODELING_PROMPT
    return AssistantAgent(
        model_client=MODEL_CLIENT,
        name="WorkflowModeler",
        description="一个能够根据步骤序列定义计算流程的智能体",
        system_message=WMPrompt,
        output_content_type_format="json"
    )



"""
# Step3: 依赖验证
- 检查流程中，每个步骤之间是否存在循环依赖
- 检查流程中，每个步骤的输入变量是否可以从 原始输入偶 or 前置步骤的输出中 获取
- 如果检查不通过，需要调整和修改步骤序列，确保没有循环依赖和未定义的输入变量
"""
def get_DependencyVerifier():
    DVPrompt = DEPENDENCY_VERIFICATION_PROMPT
    return AssistantAgent(
        model_client=MODEL_CLIENT,
        name="DependencyVerifier",
        description="一个能够检查计算流程中每个步骤的依赖关系是否符合要求的智能体",
        system_message=DVPrompt,
        output_content_type_format="json"
    )


"""
# Step4: 代码生成
- 根据前面生成的步骤序列，生成一段整体的计算代码
- 代码用Python实现，注释中需要标明各个步骤的代码在哪里开始执行
- 每个步骤结尾的位置，用 yield 语句返回当前步骤的输出，作为可追溯的依据
- 代码需要包含必要的注释，说明每个步骤的执行逻
- 最终输出项用 return 语句返回
"""

def get_CodeGenerator():
    CGPrompt = CODE_GENERATION_PROMPT
    return AssistantAgent(
        model_client=MODEL_CLIENT,
        name="CodeGenerator",
        description="一个能够根据步骤序列生成计算代码的智能体",
        system_message=CGPrompt,
        output_content_type_format="python"
    )




def get_Extractor():
    EPrompt = EXTRACT_PARAMETERS_PROMPT
    return AssistantAgent(
        model_client=MODEL_CLIENT,
        name="Extractor",
        description="一个能够从文本信息中提取计算代码中所有需要参数的智能体",
        system_message=EPrompt,
        output_content_type_format="json"
    )

