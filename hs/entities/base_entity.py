from pydantic_yaml import YamlModel

def to_kebab_case(s: str) -> str:
    return s.replace("_", "-")


class BaseEntity(YamlModel):
    #todo: do we need to write YAMLs?
    # def serialize(self, path):
    #     """
    #     Use this method to save an entity to YAML.
    #     It uses field aliases.
    #     """
    #     obj = self.yaml(by_alias=True)
    #     with open(path, 'w') as f:
    #         f.write(obj)
    #     return obj

    def to_yaml(self):
        return self.yaml(by_alias=True)

    class Config:
        alias_generator = to_kebab_case
        allow_population_by_field_name = True