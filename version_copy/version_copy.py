import shotgun_api3
import pprint


def format_version_display_info(post_data, sg_version):
    data = {
        "project_id": post_data["project_id"],
        "user_id": post_data["user_id"],
        "version_data": {
            "code": sg_version["code"],
            "entity": sg_version["entity"]["name"],
            "sg_task": sg_version["sg_task"]["name"],
            "description": sg_version["description"],
            "user_id": sg_version["user.HumanUser.id"],
            "id": sg_version["id"],
        }
    }
    return data


def format_user_input(user_input):
    entities = []
    tasks = []
    clean_input = {}
    for key in user_input:
        input_data = user_input[key]

        entity, task = str(input_data).split("!", 1)
        entities.append(entity.strip())
        tasks.append(task.strip())

        clean_input[key] = {
            "entity": entity.strip(),
            "task": task.strip(),
        }
    return entities, tasks, clean_input


def get_copy_tasks(entity_names, task_names, project_id, sg):
    print(entity_names)
    filter_asset = [
        ["project.Project.id", "is", project_id],
        ["entity.Asset.code", "in", entity_names],
        # ["content", "in", task_names],
    ]
    filter_shots = [
        ["project.Project.id", "is", project_id],
        ["entity.Shot.code", "in", entity_names],
        ["content", "in", task_names],
    ]
    fields = ["entity", "content"]

    sg_asset_tasks = sg.find("Task", filter_asset, fields)
    sg_shot_tasks = sg.find("Task", filter_shots, fields)
    return sg_asset_tasks + sg_shot_tasks


def validate_user_input(input, tasks):
    correct = []
    incorrect = []
    sg_input_data = {}

    for key in input:
        input_task = input[key]["task"]
        input_entity = input[key]["entity"]
        for task in tasks:
            if task["content"] == input_task and task["entity"]["name"] == input_entity:
                sg_input_data[key] = {"task": task}
                correct.append(key)
                continue
            else:
                continue

        if key not in correct:
            incorrect.append(key)

    return correct, incorrect, sg_input_data


def get_copy_version_data(sg, version_id):
    filter_ = [
        ["id", "is", version_id],
    ]
    fields = [
        "code",
        "user",
        "entity",
        "sg_task",
        "description",
        "image",
        "sg_status_list",
        "sg_path_to_frames",
        "sg_path_to_movie",
        "tags",
    ]
    return sg.find_one("Version", filter_, fields)


def copy_version(input_data, sg_version, sg_project, sg):
    # TODO
    batch_dicts = []
    for key in input_data:
        dict_ = get_batch_dict(sg_version, input_data[key], sg_project)


def get_batch_dict(sg_version, input_data, sg_project):
    new_version_name = sg_version["code"] + "_copy"
    new_version_desc = "Copy of version {}. Original description: {}".format(sg_version["code"], sg_version["description"])
    new_version = {
        "project": sg_project,
        "code": sg_version["code"] + "_copy",
        "description": new_version_desc,
        "user": sg_version["user"],
        "sg_status_list": sg_version["sg_status_list"],
        "sg_path_to_frames": sg_version["sg_path_to_frames"],
        "sg_path_to_movie": sg_version["sg_path_to_movie"],
        "tags": sg_version["tags"],
        "entity": input_data["task"]["entity"],
        "task": {"type": "Task", "id": input_data["task"]["id"]}

    }
    pass
