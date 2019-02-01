class DockerImage:
    def __init__(self, name, tag):
        self.tag = tag
        self.name = name

    def fullname(self):
        return self.name + ":" + self.tag

    @staticmethod
    def parse_fullname(image):
        segments = image.split(":")
        if len(segments) != 2:
            raise ValueError("Incorrect image {}".format(image))
        return DockerImage(segments[0], segments[1])
