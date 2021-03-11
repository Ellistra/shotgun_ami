import os
import urllib.request

from common.exceptions import ShotgunBatchError, ShotgunUploadError
import common.utils


def format_version_display_info(post_data, sg_version):
    """
    Formats the display data for the shotgun version to be copied.
    Args:
        post_data: POST data sent by the Shotgun website when AMI was activated
        sg_version(dict): Shotgun version dict

    Returns: Cleanly formatted dict.

    """
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
    """
    Formats the user input data into a more easily parsed dictionary.
    Args:
        user_input(dict): User input data dictionary

    Returns:    entities - List of shots/assets from user input
                tasks - list of task names from user input
                clean_input - Dict of clean user input data

    """
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
    """
    Gets tasks from user input
    Args:
        entity_names(list): Names of Shots/Assets
        task_names(list): Names of Tasks
        project_id(int): Project Shotgun ID
        sg: Shotgun connection object

    Returns: Any asset or shot tasks that could be found

    """
    filter_asset = [
        ["project.Project.id", "is", project_id],
        ["entity.Asset.code", "in", entity_names],
        ["content", "in", task_names],
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
    """
    Validates user input, confirms if shots or tasks stated exist in Shotgun.
    Args:
        input(dict): User input dictionary
        tasks(list): List of shotgun task dictionaries

    Returns:    correct - List of row numbers for correct user inputs
                incorrect - List of row numbers for incorrect user inputs
                sg_input_data - Dict of formatted data, key = sg_task

    """
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

        if key not in correct:
            incorrect.append(key)

    return set(correct), set(incorrect), sg_input_data


def get_copy_version_data(sg, version_id):
    """
    Get data for the version to be copied
    Args:
        sg: Shotgun connection object
        version_id(int): Shotgun version ID

    Returns: Shotgun dictionary for version matching the given ID

    """
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
        "sg_uploaded_movie",
        "tags",
    ]
    return sg.find_one("Version", filter_, fields)


def get_batch_dict(sg_version, input_data, sg_project):
    """
    Construct batch creation dict from the given input data
    Args:
        sg_version(dict): Shotgun dictionary of the version to be copied
        input_data(dict): Shotgun task dictionary for task in user input
        sg_project(dict): Shotgun project dictionary

    Returns: Batch data dictionary for batch creating version

    """
    data = {
        "project": sg_project,
        "code": sg_version["code"] + "_copy",
        "description": "Copy of version {}. Original description: {}".format(sg_version["code"], sg_version["description"]),
        "user": sg_version["user"],
        "sg_status_list": sg_version["sg_status_list"],
        "sg_path_to_frames": sg_version["sg_path_to_frames"],
        "sg_path_to_movie": sg_version["sg_path_to_movie"],
        "tags": sg_version["tags"],
        "entity": input_data["task"]["entity"],
        "sg_task": {"type": "Task", "id": input_data["task"]["id"]}

    }
    batch_data = {
            "request_type": "create",
            "entity_type": "Version",
            "data": data,
        }

    return batch_data


def upload_media(version_ids, original_version, sg):
    """
    Uploads media from the given version to versions represented by version_ids
    Args:
        version_ids(list): List of version ids to upload media to
        original_version(dict): Shotgun version dictionary for version being copied
        sg: Shotgun connection object

    Returns: List of successful version uploads.

    """
    url = original_version["sg_uploaded_movie"]["url"]
    name = original_version["sg_uploaded_movie"]["name"]

    success = []
    with common.utils.temporary_dir() as temp_dir:
        temp_file = os.path.join(temp_dir, name)
        urllib.request.urlretrieve(url, temp_file)
        for id_ in version_ids:
            sg.upload("Version", id_, temp_file, field_name="sg_uploaded_movie")
            success.append(id_)
    return success


def copy_version(input_data, sg_version, sg_project, sg, logger):
    """
    Copy the original version to user input locations
    Args:
        input_data(dict): User input data
        sg_version(dict): Shotgun version dict for version being copied
        sg_project(dict): Shotgun version dict for Project
        sg: Shotgun connection entity
        logger: Logging logger object

    Returns: List of Shotgun ID's of newly created versions.

    """
    batch_dicts = []
    logger.debug(
        "Getting batch dictionaries for new versions."
    )
    # Getting batch creation dictionaries
    for key in input_data:
        dict_ = get_batch_dict(sg_version, input_data[key], sg_project)
        batch_dicts.append(dict_)

    logger.debug(
        "Beginning version batch creation."
    )
    # Trying to create versions
    try:
        versions = sg.batch(batch_dicts)
    except Exception as e:
        logger.exception(
            "Encountered exception while batch creating new versions: \n{}".format(e)
        )
        raise ShotgunBatchError("Encountered error batch updating shotgun: {}".format(e))

    new_version_ids = [version["id"] for version in versions]
    logger.info(
        "Created {} versions. New ids: \n{}".format(len(new_version_ids), new_version_ids)
    )

    # Trying to upload media
    try:
        upload_media(new_version_ids, sg_version, sg)
    except Exception as e:
        logger.exception(
            "Encountered exception uploading version media: \n {}".format(e)
        )
        raise ShotgunUploadError("Encountered error uploading media to Shotgun: {}".format(e))

    return new_version_ids



