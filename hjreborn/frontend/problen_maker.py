from hjreborn.frontend.utils import con
import os
import shutil
import time
import re
import parse
import simplejson
import uuid


def gen_uuid():
    return str(uuid.uuid4())


def main():
    con.print(con.mark("HelloJudger Reborn 题目快速制作工具").bold())

    con.chapter("保存路径")

    save_path = ""

    while True:
        save_path = con.input("保存路径")
        if os.path.isdir(save_path):
            save_path = os.path.abspath(save_path)
            if len(os.listdir(save_path)) != 0:
                if not con.confirm(
                    "题目目录不为空，将清除题目目录原有的所有数据，是否继续？",
                    default=True,
                ):
                    con.log_err("题目目录不为空，请重新输入。")
                    continue
            break
        else:
            con.log_err("路径不存在，请重新输入。")

    with con.status("正在清理题目目录..."):
        shutil.rmtree(save_path)
        os.mkdir(save_path)

    con.chapter("基础信息")

    ans = {"statements": []}

    name = con.input("题目名称", default="未命名题目")
    type_ = con.input("题目类型", choice=["traditional"], default="traditional")

    con.chapter("测试点配置")
    data_path = ""
    while True:
        data_path = con.input("测试点目录路径")
        if os.path.isdir(data_path):
            data_path = os.path.abspath(data_path)
            break
        con.log_err("路径不存在，请重新输入。")

    with con.status("正在复制测试点目录..."):
        os.mkdir(os.path.join(save_path, "data"))
        for i in os.listdir(data_path):
            if os.path.isfile(os.path.join(data_path, i)):
                if i.endswith(".in") or i.endswith(".out") or i.endswith(".ans"):
                    shutil.copyfile(
                        os.path.join(data_path, i), os.path.join(save_path, "data", i)
                    )
                    # time.sleep(1 / 20)
    con.log_success("复制测试点目录成功。")
    subtasks = []
    if True:
        subtask_mode = con.input(
            "计划添加的子任务数量（single/s：一个，multi/m：多个）",
            default="single",
            choice=["single", "multi", "s", "m"],
        )
        if subtask_mode == "s":
            subtask_mode = "single"
        if subtask_mode == "single":
            input_format = con.input(
                "输入文件名的格式（使用 * 作为数据点编号的占位符）", default="*.in"
            )
            output_format = con.input(
                "输出文件名的格式（使用 * 作为数据点编号的占位符）", default="*.out"
            )
            input_format = input_format.replace("*", "{:d}")
            output_format = output_format.replace("*", "{:d}")
            listdir = os.listdir(os.path.join(save_path, "data"))
            matched = []
            input_data = {}
            output_data = {}
            for i in listdir:
                ret = parse.parse(input_format, i)
                if ret is not None:
                    input_data[ret[0]] = i
                ret = parse.parse(output_format, i)
                if ret is not None:
                    output_data[ret[0]] = i
            for i in input_data.keys():
                if i in output_data.keys():
                    matched.append((input_data[i], output_data[i]))

            con.log_success(f"找到 {len(matched)} 个匹配项。")

        else:
            input_format = con.input(
                "输入文件名的格式（使用 $ 作为子任务编号的占位符，* 作为数据点编号的占位符）",
                default="$-*.in",
            )
            output_format = con.input(
                "输出文件名的格式（使用 $ 作为子任务编号的占位符，* 作为数据点编号的占位符）",
                default="$-*.out",
            )
            input_format = input_format.replace("*", "{taskId:d}")
            output_format = output_format.replace("*", "{taskId:d}")
            input_format = input_format.replace("$", "{subtaskId:d}")
            output_format = output_format.replace("$", "{subtaskId:d}")
            listdir = os.listdir(os.path.join(save_path, "data"))
            matched = []
            input_data = {}
            output_data = {}
            for i in listdir:
                ret = parse.parse(input_format, i)
                if ret is not None:
                    taskId = ret["taskId"]
                    subtaskId = ret["subtaskId"]
                    input_data[(taskId, int(subtaskId))] = i
                ret = parse.parse(output_format, i)
                if ret is not None:
                    taskId = ret["taskId"]
                    subtaskId = ret["subtaskId"]
                    output_data[(taskId, int(subtaskId))] = i
            for i in input_data.keys():
                if i in output_data.keys():
                    id_ = len(subtasks)
                    if i[1] in subtasks:
                        id_ = subtasks.index(i[1])
                    else:
                        subtasks.append(i[1])
            subtasks.sort()
            for i in input_data.keys():
                if i in output_data.keys():
                    id_ = subtasks.index(i[1])
                    matched.append((input_data[i], output_data[i], id_))

            con.log_success(f"找到 {len(matched)} 个匹配项。")

    con.chapter("时空限制配置")
    time_limit = 0
    memory_limit = 0
    while True:
        time_limit = con.input("时间限制（ms）", default="1000")
        try:
            time_limit = int(time_limit)
        except ValueError:
            con.log_err("无效的时间限制，请重新输入。")
        else:
            break
    while True:
        memory_limit = con.input("空间限制（MiB）", default="512")
        try:
            memory_limit = float(memory_limit)
        except ValueError:
            con.log_err("无效的空间限制，请重新输入。")
        else:
            break

    con.chapter("比较器配置")

    checker_type = con.input(
        "比较器类型", choice=["row", "strict", "real", "testlib"], default="row"
    )
    precision = 0
    checker_path = ""

    if checker_type == "real":
        while True:
            precision = con.input("精度（小数点后位数）", default="6")
            try:
                precision = int(precision)
            except ValueError:
                con.log_err("无效的精度，请重新输入。")
            else:
                break
    if checker_type == "testlib":
        while True:
            checker_path = con.input("比较器路径", default="")
            if os.path.isfile(checker_path):
                os.mkdir(os.path.join(save_path, "libraries"))
                shutil.copyfile(
                    checker_path,
                    os.path.join(
                        save_path, "libraries", os.path.basename(checker_path)
                    ),
                )
                break
            else:
                con.log_err("路径不存在，请重新输入。")

    con.chapter("计分器配置")
    subtasks_policy = []
    scores = []
    single_type = ""
    score = 0
    if subtask_mode == "single":
        con.log_attention("现在配置全局计分器。")
        single_type = con.input(
            "全局计分器类型", choice=["max", "min", "sum"], default="sum"
        )
        score = 0
        while True:
            score = con.input("分数", default="100")
            try:
                score = int(score)
            except ValueError:
                con.log_err("无效的分数，请重新输入。")
            else:
                break
    else:
        con.log_attention("现在配置全局计分器。")
        single_type = con.input(
            "全局计分器类型", choice=["max", "min", "sum"], default="sum"
        )
        is_inherit = con.confirm("所有子任务是否都使用同一个计分器类型？", default=True)
        if is_inherit:
            sub_type = con.input(
                "子任务计分器类型", choice=["max", "min", "sum"], default="min"
            )
        # input_policy = con.input(
            # "输入子任务的编号从多少开始？", default="1", choice=["0", "1"]
        # )
        for i in range(len(subtasks)):
            con.log_attention(f"现在配置名为 {subtasks[i]} 的子任务（编号为 #{i + 1}）。")
            subtask_type = None
            if is_inherit:
                subtask_type = sub_type
            else:
                subtask_type = con.input(
                    "子任务计分器类型", choice=["max", "min", "sum"], default="min"
                )
            score = 0
            while True:
                score = con.input("子任务分数", default="10")
                try:
                    score = int(score)
                    scores.append(score)
                except ValueError:
                    con.log_err("无效的分数，请重新输入。")
                else:
                    break
            requires = []
            while True:
                requires = con.input(
                    "请输入子任务依赖，按照空格分隔，或输入 null 表示没有子任务依赖",
                    default="null",
                )
                if requires != "null":
                    try:
                        requires = [int(i) for i in requires.split()]
                    except:
                        con.log_err("无效的依赖，请重新输入。")
                    else:
                        break
                else:
                    requires = []
                    break

            subtasks_policy.append((score, subtask_type, requires))

    con.chapter("题面配置")
    if con.confirm("是否需要配置题面？", default=False):
        p_count = 0
        os.mkdir(os.path.join(save_path, "resources"))
        while True:
            p_count += 1
            p_exists = con.confirm(f"是否需要配置第 {p_count} 个题面？", default=False)
            if not p_exists:
                break
            p_name = con.input("题面名称", default=f"题面 {p_count}")
            p_type = con.input(
                "题面类型", choice=["md", "pdf", "html", "txt"], default="md"
            )
            while True:
                p_path = con.input("题面路径")
                if os.path.isfile(p_path):
                    shutil.copyfile(
                        p_path,
                        os.path.join(
                            save_path,
                            "resources",
                            gen_uuid() + os.path.split(p_path)[-1],
                        ),
                    )
                    p_path = os.path.join(
                        save_path, "resources", gen_uuid() + os.path.split(p_path)[-1]
                    )
                    break
                else:
                    con.log_err("路径不存在，请重新输入。")
            ans["statements"].append(
                {"type": p_type, "name": p_name, "path": os.path.basename(p_path)}
            )
        con.log_success("题面配置完成！")
    else:
        os.mkdir(os.path.join(save_path, "resources"))
        p_path = os.path.join(save_path, "resources", gen_uuid() + ".md")
        p_type = "md"
        p_name = "缺省题面"

        with open(p_path, "w", encoding="utf-8") as f:
            f.write(f"# {name}\n这是一个缺省题面，如果需要，请修改它。")

        ans["statements"].append(
            {"type": p_type, "name": p_name, "path": os.path.basename(p_path)}
        )

        con.log_attention("缺省题面配置完成！如有需要，请手动更改。")
    ans["name"] = name
    ans["type"] = type_
    if checker_type == "real":
        ans["judger"] = {"id": "real", "precision": precision}
    elif checker_type == "testlib":
        ans["judger"] = {"id": "testlib", "path": os.path.basename(checker_path)}
    else:
        ans["judger"] = {"id": checker_type}
    if subtask_mode == "single":
        ans["subtasks"] = [{"method": single_type, "required": []}]
        ans["all"] = {"method": "sum"}
        ans["testcases"] = []
        for j, i in enumerate(matched):
            current_mark = 0
            if single_type == "sum":
                current_mark = int(score / len(matched))
                if j == len(matched) - 1:
                    current_mark += score - int(score / len(matched)) * len(matched)
            else:
                current_mark = score
            ans["testcases"].append(
                {
                    "in": i[0],
                    "out": i[1],
                    "subtask": 1,
                    "time": time_limit,
                    "memory": int(memory_limit * 1024 * 1024),
                    "mark": current_mark,
                }
            )
        con.log_success("题目配置构建完成！")
    else:
        ans["all"] = {"method": single_type}
        ans["subtasks"] = []
        ans["testcases"] = []
        for i in range(len(subtasks_policy)):
            ans["subtasks"].append(
                {"method": subtasks_policy[i][1], "required": subtasks_policy[i][2]}
            )
        tasks_per = {}
        for i in matched:
            if i[2] not in tasks_per:
                tasks_per[i[2]] = []
            tasks_per[i[2]].append(i)
        for i in sorted(tasks_per.keys()):
            score = scores[i - 1]
            for j in range(len(tasks_per[i])):
                current_mark = 0
                if ans["subtasks"][i - 1]["method"] == "sum":
                    current_mark = int(score / len(tasks_per[i]))
                    if j == len(tasks_per[i]) - 1:
                        current_mark += score - int(score / len(tasks_per[i])) * len(
                            tasks_per[i]
                        )
                else:
                    current_mark = score
                ans["testcases"].append(
                    {
                        "in": tasks_per[i][j][0],
                        "out": tasks_per[i][j][1],
                        "subtask": i + 1,
                        "time": time_limit,
                        "memory": int(memory_limit * 1024 * 1024),
                        "mark": current_mark,
                    }
                )
        con.log_success("题目配置构建完成！")

    with open(os.path.join(save_path, "problem.json"), "w", encoding="utf-8") as f:
        simplejson.dump(ans, f, indent=4, ensure_ascii=False)
    con.log_success(f"恭喜！题目 {name} 已经配置完成！")
