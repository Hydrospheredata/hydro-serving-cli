from docker.errors import NotFound


def is_container_exists(client, container_id):
    """
    Checks if container is created
    :param client: docker client
    :param container_id: container id or name
    :return: True if container is created, False otherwise
    """
    try:
        client.containers.get(container_id)
        return True
    except NotFound:
        return False
