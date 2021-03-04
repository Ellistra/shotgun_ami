import logging
import shotgun_api3
from common.constants import ReportConstants


def get_logger(name):
    """
    Get a common logging object
        Logs debug or higher to log file
        Logs info or higher to console

    Returns: common logging logger objects

    """
    # setting up file logging
    logging.basicConfig(
        level=logging.DEBUG,
        format="%(asctime)s %(name)-12s %(levelname)-8s %(message)s",
        filename="D:\code\logs\\ami_version_copy.log",
        filemode="w"
    )

    # Setting up console logging.
    console = logging.StreamHandler()
    console.setLevel(logging.INFO)
    formatter = logging.Formatter("%(name)-12s %(levelname)-8s %(message)s")
    console.setFormatter(formatter)

    # Adding console handler
    logging.getLogger("").addHandler(console)

    # Generating name of each module's logger
    logger = logging.getLogger(name)

    return logger


def get_sg_connection():
    """
    Returns: Shotgun_api3 Shotgun object
    """
    sg = shotgun_api3.Shotgun(
        base_url=ReportConstants.shotgun_url,       # Website url. Eg. "https://dreamworks.shotgunstudio.com"
        script_name=ReportConstants.login,          # Scrip user
        api_key=ReportConstants.password,           # Script key
    )
    return sg


def get_version_from_id(sg, version_id):
    filter_ = [
        ["id", "is", version_id]
    ]
    fields = ["code", "user", "entity", "sg_task", "description", "image", "user.HumanUser.id"]
    return sg.find_one("Version", filter_, fields)


def get_user_from_id(sg, version_id):
    filter_ = [
        ["id", "is", version_id]
    ]
    fields = ["login", "name"]
    return sg.find_one("HumanUser", filter_, fields)


def get_project_from_id(sg, project_id):
    filter_ = [
        ["id", "is", project_id]
    ]
    fields = ["code"]
    return sg.find_one("Project", filter_, fields)
