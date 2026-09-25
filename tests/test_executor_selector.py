from project_brain.execution.selector import select_executor
from project_brain.tools.types import ToolKind

def test_browser_routes_to_browser():
    assert select_executor(ToolKind.BROWSER)=="browser"
