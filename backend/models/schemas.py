from dataclasses import dataclass, field
from typing import List, Dict, Any


@dataclass
class TransformationTest:
    id: str
    type: str
    description: str
    transformation_sql: str
    dummy_input_data: List[Dict[str, Any]]
    expected_output_data: List[Dict[str, Any]]
    status: str = "pending"


@dataclass
class ProcedureTestPlan:
    procedure_name: str
    procedure_sql: str
    tests: List[TransformationTest] = field(default_factory=list)
