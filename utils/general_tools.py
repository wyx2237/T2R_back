from autogen_agentchat.base import TaskResult

def debug_info_tool(result:TaskResult):
    print(f"content: \n{result.messages[-1].to_model_text()}\n")

    # 时间延迟计算
    print(f"answer created_at: \n{result.messages[-1].created_at}\n")
    print(f"delay: \n{result.messages[-1].created_at - result.messages[0].created_at}\n")
    ## token消耗计算
    print(f"models_usage: \n{result.messages[-1].models_usage}\n")

def get_result_content(result:TaskResult) -> str:
    debug_info_tool(result)
    return result.messages[-1].to_model_text()