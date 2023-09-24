# pylint:disable = all

import jsonschema
import simplejson as json
from core.signals import *
from i18n import _
import os

schema = {
    "$schema": "http://json-schema.org/draft-07/schema#",
    "$id" : "http://github.com/hellojudger/HellojudgerRreborn/problem.schema",
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
        },
        "all" : {
            "type" : "object",
            "properties" : {
                "method" : {
                    "type" : "string",
                    "enum" : ["min", "max", "sum"]
                }
            },
            "required" : ["method"]
        }
    },
    "required" : ["name", "statements", "testcases", "subtasks", "type", "judger", "all"]
}

def validate(path : str):
    path = os.path.abspath(path)
    try:
        with open("{}/problem.json".format(path), "r", encoding="utf-8") as f:
            problem = json.load(f)
    except Exception as e:
        return ProblemFileInvalid(repr(e))
    try:
        jsonschema.validate(problem, schema)
    except jsonschema.ValidationError as err:
        return ProblemFileInvalid(str(err))
    if problem["type"] == "interactive_noip" and problem.get("interactive_library") is None:
        return ProblemFileInvalid(_("core.problem_validator.interactiveNoLibrary").format(lib = problem.get("interactive_library")))
    if problem["type"] == "interactive_noip":
        if not os.path.isfile("{}/libraries/{}".format(path, problem.get("interactive_library"))):
            return ProblemFileInvalid(_("core.problem_validator.interactiveLibraryNotFound"))
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
    if not problem["judger"]["id"] == "testlib" and os.path.isfile("{}/libraries/{}".format(path, problem["judger"].get("path"))):
        return ProblemFileInvalid(_("core.problem_validator.testlibJudgerNotFound").format(lib = problem["judger"].get("path")))
    for i in problem["statements"]:
        if not os.path.isfile("{}/resources/{}".format(path, i["path"])):
            return ProblemFileInvalid(_("core.problem_validator.statementNotFound").format(path = i["path"]))
    for i in problem["testcases"]:
        if not os.path.isfile("{}/data/{}".format(path, i["in"])):
            return ProblemFileInvalid(_("core.problem_validator.inNotFound").format(inf = i["in"]))
        if not os.path.isfile("{}/data/{}".format(path, i["out"])):
            return ProblemFileInvalid(_("core.problem_validator.outNotFound").format(ouf = i["out"]))
    return ProblemFileValid(_("core.problem_validator.pfv"))
