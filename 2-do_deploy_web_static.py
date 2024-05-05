#!/usr/bin/python3
# a Fabric script (based on the file `1-pack_web_static.py`) that
# distributes an archive to your web servers, using the function `do_deploy`

from fabric.api import env, put, run, sudo
# Import os for path manipulation (optional, depending on your implementation)
import os


def do_deploy(archive_path):
    """
    Deploys the provided archive to web servers.

    Args:
        archive_path: Path to the archive file.

    Returns:
        bool: True if deployment is successful, False otherwise.
    """

    if not os.path.exists(archive_path):
        print(f"Error: Archive file {archive_path} does not exist.")
        return False

    # Define web server IPs
    env.hosts = ['52.91.126.218', '54.89.178.237']

    # Upload archive to temporary directory on each server
    with put(archive_path, "/tmp/") as result:
        if not result.ok:
            print(f"Failed to upload archive: {result.failed}")
            return False

    # Extract archive on each server
    for server in env.hosts:
        # Create release directory
        run(f"""mkdir -p /data/web_static/releases/{
            os.path.basename(archive_path).split('.')[0]}""")

        run(f"""tar -xzf /tmp/{os.path.basename(archive_path)} -C
            /data/web_static/releases/{
                os.path.basename(archive_path).split('.')[0]}""")

    # Clean up temporary archive on each server
    run("rm /tmp/*.tgz")

    # Update symbolic link and directories on each server
    for server in env.hosts:
        # Delete old current link
        run("rm -rf /data/web_static/current")

        # Move content to release directory
        run("""mv /data/web_static/releases/{}/web_static/*
            /data/web_static/releases/{}""".format(
                os.path.basename(archive_path).split('.')[0],
                os.path.basename(archive_path).split('.')[0]))

        # Remove empty web_static directory
        run("rm -rf /data/web_static/releases/{}/web_static".format(
            os.path.basename(archive_path).split('.')[0]))

        # Create new current link
        run("""ln -s /data/web_static/releases/{}
            /data/web_static/current""".format(
                os.path.basename(archive_path).split('.')[0]))

    print("New version deployed!")
    return True
