from flask import Flask, request, render_template

from common import utils
from common.exceptions import ShotgunBatchError, ShotgunUploadError
import version_copy

LOGGER = utils.get_logger("version_copy_app")
app = Flask(__name__)


@app.route("/version/copy", methods=["GET", "POST"])
def version_copy_app():
    """ Shotgun Version Copy AMI main entrypoint. Renders version copy html template """
    # Getting logger
    LOGGER.info("Started version copy app.")

    # getting post data
    post_data = request.form

    # Checking version ids. Tool only supports copying a single version at a time.
    version_ids = post_data["selected_ids"].split(",")
    if len(version_ids) > 1:
        LOGGER.info("More than one ID selected. Exiting.")
        return "<strong>Version copy only supports one version at a time. Please select a single version and try again."

    # Getting shotgun version dict.
    sg = utils.get_sg_connection()
    sg_version = utils.get_version_from_id(sg, int(version_ids[0]))

    # Formatting data to send to template
    copy_data = version_copy.format_version_display_info(post_data, sg_version)
    LOGGER.info("Got display data for version {}, rendering template.".format(sg_version["code"]))

    return render_template("version_copy.html", posts=copy_data)


@app.route("/version/copy/validate", methods=["POST"])
def version_copy_validate_app():
    """ Validation entry point for version copy AMI. Validates and returns errors, or creates versions of no errors """
    post_data = request.form
    LOGGER.info("Starting version copy validation. Posts: \n {}".format(post_data))

    # Getting user input data into its own dict.
    user_input = {}
    for key in post_data.keys():
        if key in ["project_id", "user_id", "version_id"]:
            continue
        user_input[key] = post_data[key]

    # Post data will always enter something for user input, check if data is valid.
    if len(user_input) <= 1 and user_input["1"] == "!":
        LOGGER.info("No user input entered. Exiting.")
        return "NO_DATA"

    # Formatting user input data for easier handling
    entities, tasks, clean_input = version_copy.format_user_input(user_input)
    LOGGER.info("Cleaned up user input: \n{}".format(clean_input))

    # Getting Shotgun tasks and shots from user input.
    sg = utils.get_sg_connection()
    project_id = int(post_data["project_id"])
    sg_tasks = version_copy.get_copy_tasks(entities, tasks, project_id, sg)

    # Validating user input data.
    LOGGER.info("Beginning validation on user input data: \n{}".format(user_input))
    correct, errors, sg_input_data = version_copy.validate_user_input(clean_input, sg_tasks)
    LOGGER.info("Correct: {}, Incorrect: {}".format(correct, errors))

    # Returning errors to version copy page if validation fails on any entries.
    if errors:
        LOGGER.error("User input contained errors. Returning validation data.")
        return "+".join(errors)

    LOGGER.info("Validation passed. Creating new versions.")
    version_id = int(post_data["version_id"])
    sg_version = version_copy.get_copy_version_data(sg, version_id)
    sg_project = utils.get_project_from_id(sg, project_id)

    # Try creating new versions, catch any known errors.
    try:
        version_ids = version_copy.copy_version(sg_input_data, sg_version, sg_project, sg, LOGGER)
    except ShotgunBatchError as sbe:
        LOGGER.exception(
            "Got an exception while creating new versions: \n{}".format(sbe)
        )
        return "ERROR_BATCH"
    except ShotgunUploadError as sue:
        LOGGER.exception(
            "Got an exception while uploading version attachments: \n{}".format(sue)
        )
        return "ERROR_ATT"
    except Exception as e:
        LOGGER.exception("Got an exception while creating new versions: \n{}".format(e))
        return "ERROR_CR"

    # If sending notifications, can insert that function here.
    LOGGER.info("Copy version complete. New version ids: {}".format(version_ids))
    return "0"


if __name__ == '__main__':
    app.run(port=5000)
