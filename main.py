# pylint:disable = all

from core.problem_validator import validate_format
from i18n import switch_language

switch_language("zh_CN")

print(validate_format({
    "name" : "测试题目",
    "statements" : [
        {
            "type" : "md",
            "path" : "1.md",
            "name" : "题面 1"
        }
    ],
    "testcases" : [
        {
            "in" : "1.in",
            "out" : "1.out",
            "time" : 1000,
            "memory" : 1073741824,
            "mark" : 100,
            "subtask" : 1
        }
    ],
    "subtasks" : [
        {
            "method" : "sum",
            "required" : []
        }
    ],
    "type" : "traditional",
    "judger" : {
        "id" : "row"
    }
}))