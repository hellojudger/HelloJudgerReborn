# pylint:disable = all

import jsonschema
from core.signals import ProblemFileInvalid, ProblemFileValid
from i18n import _

schema = {
    "$schema": "http://json-schema.org/draft-07/schema#",
    "$id" : "hellojudger/reborn/problem.schema",
    "definitions": {
        "statement" : {
            "type" : "object",
            "properties": {
                "type" : {
                    "type" : "string",
                    "enum" : ["md", "pdf", "html", "txt"]
                },
                "name" : {
                    "type" : "string"
                },
                "path" : {
                    "type" : "string"
                }
            },
            "required" : ["type", "path"]
        },
        "testcase" : {
            "type" : "object",
            "properties": {
                "in" : {"type" : "string"},
                "out" : {"type" : "string"},
                "time" : {
                    "type" : "integer",
                    "minimum": 0,
                    "maximum": 31536000000
                },
                "memory" : {
                    "type" : "integer",
                    "minimum": 0,
                    "maximum": 1099511627776
                },
                "mark" : {
                    "type" : "number",
                    "minimum": 0,
                    "maximum": 2147483648
                },
                "subtask" : {
                    "type" : "integer",
                    "minimum": 1,
                    "maximum": 1024
                }
            },
            "required" : ["in", "out", "memory", "time", "mark", "subtask"]
        },
        "subtask" : {
            "type" : "object",
            "properties": {
                "method" : {
                    "type" : "string",
                    "enum" : ["min", "max", "sum"]
                },
                "required" : {
                    "type" : "array",
                    "items" : [{
                        "type" : "integer",
                        "minimum": 1,
                        "maximum": 1024
                    }],
                    "minItems" : 0,
                    "maxItems" : 1024
                }
            },
            "required" : ["required", "method"]
        },
        "judger" : {
            "type" : "object",
            "properties": {
                "id" : {
                    "type" : "string",
                    "enum" : ["row", "strict", "real", "testlib"]
                },
                "precision" : {
                    "type" : "integer",
                    "minimum": 0,
                    "maximum": 18
                },
                "path" : {
                    "type" : "string",
                    "minLength" : 1,
                    "maxLength": 65535
                }
            },
            "required": ["id"]
        }
    },
    "properties": {
        "name" : {
            "type" : "string",
            "minLength" : 1,
            "maxLength" : 65535
        },
        "statements" : {
            "type" : "array",
            "items" : [{"$ref" : "#/definitions/statement"}],
            "minItems" : 1,
            "maxItems" : 1024
        },
        "testcases" : {
            "type" : "array",
            "items" : [{"$ref" : "#/definitions/testcase"}],
            "minItems" : 1,
            "maxItems" : 1024
        },
        "subtasks" : {
            "type" : "array",
            "items" : [{"$ref" : "#/definitions/subtask"}],
            "minItems" : 1,
            "maxItems" : 1024
        },
        "type" : {
            "type" : "string",
            "enum" : ["traditional", "interactive_noi"]
        },
        "judger" : {
            "$ref" : "#/definitions/judger"
        },
        "interactive_library" : {
            "type" : "string",
            "minLength" : 1,
            "maxLength" : 65535
        }
    },
    "required" : ["name", "statements", "testcases", "subtasks", "type", "judger"]
}

def validate_format(problem : dict):
    try:
        jsonschema.validate(problem, schema)
    except jsonschema.ValidationError as err:
        return ProblemFileInvalid(str(err))
    if problem["type"] == "interactive_noip" and problem.get("interactive_library") is None:
        return ProblemFileInvalid(_("core.problem_validator.interactiveNoLibrary"))
    for i in problem["testcases"]:
        if i["subtask"] > len(problem["subtasks"]):
            return ProblemFileInvalid(_("core.problem_validator.subtaskIdInvalid").format(sid = i["subtask"]))
    for cnt, i in enumerate(problem["subtasks"]):
        for j in i["required"]:
            if j >= cnt + 1:
                return ProblemFileInvalid(_("core.problem_validator.subtaskIdInvalidInRequired").format(sid = cnt + 1))
    if problem["judger"]["id"] == "real" and problem["judger"].get("precision") is None:
        return ProblemFileInvalid(_("core.problem_validator.realJudgerWithoutPrecision"))
    if problem["judger"]["id"] == "testlib" and problem["judger"].get("path") is None:
        return ProblemFileInvalid(_("core.problem_validator.testlibJudgerWithoutPath"))
    return ProblemFileValid(_("core.problem_validator.pfv"))
