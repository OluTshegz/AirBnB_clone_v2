#!/usr/bin/python3
# a Fabric script (based on the file `1-pack_web_static.py`) that
# distributes an archive to your web servers, using the function `do_deploy`

from fabric.api import env, put, run
# Import os for path manipulation (optional, depending on your implementation)
import os


def do_deploy(archive_path):
    """
    Deploys the provided archive to web servers.

    Args:
        archive_path (str): Path to the archive file.

    Returns:
        bool: True if deployment is successful, False otherwise.
    """

    if not os.path.exists(archive_path):
        print(f"Error: Archive file {archive_path} does not exist.")
        return False

    # Define web server IPs
    env.hosts = ['52.91.126.218', '54.89.178.237']

    file_name = os.path.basename(archive_path)
    folder_name = file_name.replace(".tgz", "")
    folder_path = "/data/web_static/releases/{}/".format(folder_name)
    success = False

    try:
        # Upload archive to temporary directory
        with put(archive_path, f"/tmp/{file_name}") as result:
            if not result.ok:
                print(f"Failed to upload archive: {result.failed}")
                return False

        # Extract archive
        # Create release directory
        run(f"""mkdir -p /data/web_static/releases/{folder_path}""")

        run(f"""tar -xzf /tmp/{file_name} -C {folder_path}""")

        # Clean up temporary archive
        run(f"rm -rf /tmp/{file_name}")

        # Update symbolic link and directories
        # Move content to release directory
        run(f"mv {folder_path}web_static/* {folder_path}")

        # Remove empty web_static directory
        run(f"rm -rf {folder_path}web_static")

        # Delete old current link
        run("rm -rf /data/web_static/current")

        # Create new current link
        run(f"ln -s {folder_path} /data/web_static/current")

        print("New version deployed!")
        success = True

    except Exception as e:
        print(f"Error deploying archive: {e}")
        success = False

    return success
