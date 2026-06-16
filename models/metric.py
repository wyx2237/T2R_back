"""指标管理相关 Pydantic 模型，对应 API.md §2 + 附录 Metric 类型"""

from pydantic import BaseModel


class WorkflowInput(BaseModel):
    input_name: str
    input_desc: str
    input_type: str


class WorkflowOutput(BaseModel):
    output_name: str
    output_desc: str
    output_type: str
    output_unit: str


class StepInput(BaseModel):
    input_name: str
    input_desc: str
    input_type: str
    input_source: str  # "$|inputs|.xxx" 或 "$|steps|.N.output_name"


class StepOutput(BaseModel):
    output_name: str
    output_desc: str
    output_type: str


class WorkflowStep(BaseModel):
    step_id: str
    step_name: str
    step_description: str
    step_inputs: list[StepInput]
    step_outputs: list[StepOutput]
    category: str
    reason: str
    detail: str


class Metric(BaseModel):
    id: str
    code: str
    department: str
    reference: str
    name: str
    description: str
    inputs: list[WorkflowInput]
    output: WorkflowOutput
    steps: list[WorkflowStep]
    executableCode: str


class CreateMetricRequest(BaseModel):
    question: str
    formula: str
