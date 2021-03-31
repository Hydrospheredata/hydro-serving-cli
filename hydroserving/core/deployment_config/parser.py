import logging
import copy
import functools
from typing import Callable, List, Optional, Dict

from hydrosdk.cluster import Cluster
from hydrosdk.deployment_configuration import *
from hydrosdk.utils import handle_request_error
from hydrosdk.builder import AbstractBuilder

from hydroserving.util.parseutil import fill_arguments


def __parse_deploymet_configuration_with_cheating(in_dict: dict) -> Callable[[Cluster], DeploymentConfiguration]:
    """
    You can submit a deployment configuration to the cluster without 
    any downline validation by issuing this method.

    Don't do this, this is cheating.
    """
    class LocalBuilder(AbstractBuilder):
        def __init__(self, in_dict: dict) -> 'LocalBuilder':
            raw_dict = copy.deepcopy(in_dict)
            del raw_dict['kind']
            self.raw_dict = raw_dict

        def build(self, cluster: Cluster) -> DeploymentConfiguration:
            resp = cluster.request("POST", DeploymentConfiguration._BASE_URL, json=raw_dict)
            handle_request_error(
                resp, f"Failed to upload new Deployment Configuration. {resp.status_code} {resp.text}")
            return DeploymentConfiguration.from_camel_case_dict(resp.json())
    
    return functools.partial(
        fill_arguments(lambda **kwargs: LocalBuilder(in_dict)),
    )
    

def parse_deployment_configuration(in_dict: dict) -> Callable[[Cluster], DeploymentConfiguration]:
    """
    Parse deployment configuration from yaml

    kind: DeploymentConfiguration
    name: config
    hpa:
      ...
    deployment:
      ...
    container:
      ...
    pod:
      ...
    """
    return functools.partial(
        fill_arguments,
        lambda **kwargs: DeploymentConfigurationBuilder(in_dict["name"]) \
            ._with_hpa_spec(_parse_horizontal_pod_autoscaler_spec(in_dict.get("hpa"))) \
            ._with_deployment_spec(_parse_deployment_spec(in_dict.get("deployment"))) \
            ._with_container_spec(_parse_container_spec(in_dict.get("container"))) \
            ._with_pod_spec(_parse_pod_spec(in_dict.get("pod")))
    )


def _parse_horizontal_pod_autoscaler_spec(in_dict: dict) -> Optional[HorizontalPodAutoScalerSpec]:
    """
    Parse HorizontalPodAutoscalerSpec.
    
    hpa:
      minReplicas: 1
      maxReplicas: 4
      cpuUtilization: 80
    """
    logging.debug(f"Parsing horizontal pod autoscaler specification: {in_dict}")
    if in_dict is None: 
        logging.debug("Couldn't find horizontal pod autoscaler specification, skipping")
        return None 
    hpa = HorizontalPodAutoScalerSpec(
        min_replicas=in_dict.get("minReplicas"),
        max_replicas=in_dict.get("maxReplicas"),
        cpu_utilization=in_dict.get("cpuUtilization")
    )
    logging.debug(f"Parsed horizontal pod autoscaler specification: {hpa}")
    return hpa


def _parse_deployment_spec(in_dict: Optional[dict]) -> Optional[DeploymentSpec]:
    """
    Parse DeploymentSpec.

    deployment:
      replicaCount: 2
    """
    logging.debug(f"Parsing deployment specification: {in_dict}")
    if in_dict is None: 
        logging.debug("Couldn't find deployment specification, skipping")
        return None 
    deployment = DeploymentSpec(replica_count=in_dict.get("replicaCount"))
    logging.debug(f"Parsed deployment specification: {deployment}")
    return deployment


def _parse_container_spec(in_dict: Optional[dict]) -> Optional[ContainerSpec]:
    """
    Parse ContainerSpec.

    container:
      resources:
        limits:
          cpu: 500m
          memory: 2G
        requests:
          cpu: 250m
          memory: 1G
      env:
        foo: bar
        bar: que
    """
    logging.debug(f"Parsing container specification: {in_dict}")
    if in_dict is None: 
        logging.debug("Couldn't find container specification, skipping")
        return None
    container = ContainerSpec(
        resources=ResourceRequirements(
            limits=in_dict.get("resources", {}).get("limits"),
            requests=in_dict.get("resources", {}).get("requests")
        ),
        env=in_dict.get("env")
    )
    logging.debug(f"Parsed container specification: {container}")
    return container


def _parse_pod_spec(in_dict: Optional[dict]) -> Optional[PodSpec]:
    """
    Parse PodSpec.

    pod:
      nodeSelector:
        ...
      affinity:
        ...
      tolerations:
        ...
    """
    logging.debug(f"Parsing pod specification: {in_dict}")
    if in_dict is None: 
        logging.debug("Couldn't find pod specification, skipping")
        return None
    pod = PodSpec(
        node_selector=_parse_node_selector(in_dict.get("nodeSelector")),
        affinity=_parse_affinity(in_dict.get("affinity")),
        tolerations=_parse_tolerations(in_dict.get("tolerations"))
    )
    logging.debug(f"Parsed pod specification: {pod}")
    return pod


def _parse_tolerations(items: List[dict]) -> List[Toleration]:
    """
    Parse Toleration.

    tolerations:
      - effect: PreferNoSchedule
        key: equalToleration
        tolerationSeconds: 30
        operator: Equal
        value: foo
      - key: equalToleration
        operator: Exists
        effect: PreferNoSchedule
        tolerationSeconds: 30
    """
    logging.debug(f"Parsing tolerations: {items}")
    tolerations = []
    for item in items:
        tolerations.append(
            Toleration(
                operator=item.get("operator"),
                toleration_seconds=item.get("tolerationSeconds"),
                key=item.get("key"),
                value=item.get("value"),
                effect=item.get("effect")
            )
        )
    if tolerations:
        logging.debug(f"Parsed tolerations: {tolerations}")
    else:
        logging.debug("Couldn't find any tolerations")
    return tolerations


def _parse_node_affinity_node_selector(in_dict: Optional[dict] = None) -> Optional[NodeSelector]:
    """
    Parse node affinity NodeSelector.

    nodeSelectorTerms:
      ...
    """
    logging.debug(f"Parsing node affinity node selector: {in_dict}")
    if in_dict is None:
        logging.debug("Couldn't find any node affinity node selector, skipping")
        return None
    node_selector = NodeSelector(
        node_selector_terms=[
            _parse_node_selector_term(t) 
            for t in in_dict.get("nodeSelectorTerms", [])
        ]
    )
    logging.debug(f"Parsed node affinity node selector: {node_selector}")
    return node_selector


def _parse_node_selector(in_dict: Optional[dict] = None) -> Optional[Dict[str, str]]:
    """
    Parse NodeSelector constraints.

    nodeSelector:
      im: a_map
      foo: bar
    """
    logging.debug(f"Parsing node selectors: {in_dict}")
    if in_dict is None:
        logging.debug("Couldn't find any node selector constraints, skipping")
        return None
    constraints = in_dict
    logging.debug(f"Parsed node selector constraints: {constraints}")
    return constraints


def _parse_affinity(in_dict: Optional[dict] = None) -> Optional[Affinity]:
    """
    Parse AffinitySpec.

    affinity:
        nodeAffinity:
          ...
        podAffinity:
          ...
        podAntiAffinity:
          ...
    """
    logging.debug(f"Parsing affinity: {in_dict}")
    if in_dict is None:
        logging.debug("Couldn't find affinity specification, skipping")
        return None
    affinity = Affinity(
        node_affinity=_parse_node_affinity(in_dict.get("nodeAffinity")),
        pod_affinity=_parse_pod_affinity(in_dict.get("podAffinity")),
        pod_anti_affinity=_parse_pod_anti_affinity(in_dict.get("podAntiAffinity"))
    )
    logging.debug(f"Parsed affinity: {affinity}")
    return affinity


def _parse_node_affinity(in_dict: Optional[dict] = None) -> Optional[NodeAffinity]:
    """
    Parse NodeAffinity.

    nodeAffinity:
      requiredDuringSchedulingIgnoredDuringExecution:
        nodeSelectorTerms:
          ...
      preferredDuringSchedulingIgnoredDuringExecution:
        ...
    """
    logging.debug(f"Parsing node affinity: {in_dict}")
    if in_dict is None:
        logging.debug("Couldn't find node affinity specification, skipping")
        return None
    required_terms = in_dict.get("requiredDuringSchedulingIgnoredDuringExecution", {})
    preferred_terms = in_dict.get("preferredDuringSchedulingIgnoredDuringExecution", [])
    node_affinity = NodeAffinity(
        required_during_scheduling_ignored_during_execution=_parse_node_affinity_node_selector(required_terms),
        preferred_during_scheduling_ignored_during_execution=_parse_preferred_scheduling_terms(preferred_terms)
    )
    logging.debug(f"Parsed node affinity: {node_affinity}")
    return node_affinity


def _parse_node_selector_term(in_dict: dict) -> NodeSelectorTerm:
    """
    Parse NodeSelectorTerm.

    matchExpressions:
      - key: exp1
        operator: Exists
        values: 
          - a
      matchFields:
      - key: fields1
        operator: Exists
        values:
          - b
    """
    logging.debug(f"Parsing node selector term: {in_dict}")
    expressions = []
    for exp in in_dict.get("matchExpressions", []):
        expressions.append(NodeSelectorRequirement(
            key=exp.get("key"), 
            operator=exp.get("operator"), 
            values=exp.get("values")
        ))
    fields = []
    for field in in_dict.get("matchFields", []):
        fields.append(NodeSelectorRequirement(
            key=field.get("key"), 
            operator=field.get("operator"),
            values=exp.get("values")
        ))
    term = NodeSelectorTerm(
        match_expressions=expressions,
        match_fields=fields
    )
    logging.debug(f"Parsed node selector term: {term}")
    return term


def _parse_preferred_scheduling_terms(items: List[dict]) -> List[PreferredSchedulingTerm]:
    """
    Parse PreferredSchedulingTerm.

    - preference:
        matchExpressions:
          - key: expression
            operator: NotIn
            values:
              - a
        matchFields:
          - key: field
            operator: NotIn
            values:
              - b
      weight: 100
    """
    logging.debug(f"Parsing preferred scheduling terms: {items}")
    terms = []
    for item in items:
        terms.append(PreferredSchedulingTerm(
            weight=item.get("weight"), 
            preference=_parse_node_selector_term(item["preference"])
        ))
    if terms: 
        logging.debug(f"Parsed preferred scheduling terms: {terms}")
    else: 
        logging.debug("Couldn't find any preferred scheduling terms")
    return terms


def _parse_pod_affinity(in_dict: Optional[dict] = None) -> Optional[PodAffinity]:
    """
    Parse PodAffinity.

    podAffinity:
      requiredDuringSchedulingIgnoredDuringExecution:
        ...
      preferredDuringSchedulingIgnoredDuringExecution:
        ...
    """
    logging.debug(f"Parsing pod affinity: {in_dict}")
    if in_dict is None:
        logging.debug("Couldn't find pod affinity specification, skipping")
        return None
    required_terms = in_dict.get("requiredDuringSchedulingIgnoredDuringExecution", [])
    preferred_terms = in_dict.get("preferredDuringSchedulingIgnoredDuringExecution", [])
    pod_affinity = PodAffinity(
        required_during_scheduling_ignored_during_execution=[_parse_pod_affinity_term(t) for t in required_terms],
        preferred_during_scheduling_ignored_during_execution=_parse_weighted_pod_affinity_terms(preferred_terms),
    )
    logging.debug(f"Parsed pod affinity: {pod_affinity}")
    return pod_affinity  


def _parse_pod_affinity_term(in_dict: Optional[dict] = None) -> PodAffinityTerm:
    """
    Parse PodAffinityTerm.

    labelSelector:
      matchExpressions:
        - key: foo
          operator: Exists
        - key: bar
          operator: NotIn
          values:
            - a
            - b
    namespaces:
      - namespace1
    topologyKey: top
    """
    logging.debug(f"Parsing pod affinity term: {in_dict}")
    if in_dict is None:
        logging.debug("Couldn't find pod affinity term, skipping")
        return None
    term = PodAffinityTerm(
        label_selector=_parse_label_selector(in_dict.get("labelSelector")),
        topology_key=in_dict.get("topologyKey"),
        namespaces=in_dict.get("namespaces")
    )
    logging.debug(f"Parsed pod affinity terms: {term}")
    return term


def _parse_label_selector(in_dict: Optional[dict] = None) -> LabelSelector:
    """
    Parse LabelSelector.

    matchExpressions:
      - key: foo
        operator: Exists
      - key: bar
        operator: NotIn
        values:
          - a
          - b
    matchLabels:
      foo: bar
    """
    logging.debug(f"Parsing label selector: {in_dict}")
    if in_dict is None:
        logging.debug("Couldn't find label selector, skipping")
        return None
    expressions = []
    for exp in in_dict.get("matchExpressions", []):
        expressions.append(LabelSelectorRequirement(
            key=exp["key"],
            operator=exp["operator"],
            values=exp.get("values")
        ))
    selector = LabelSelector(
        match_expressions=expressions,
        match_labels=in_dict.get("matchLabels")
    )
    logging.debug(f"Parsed label selector: {selector}")
    return selector


def _parse_weighted_pod_affinity_terms(items: List[dict]) -> List[WeightedPodAffinityTerm]:
    """
    Parse WeightedPodAffinityTerm.

    - weight: 100
      podAffinityTerm:
        labelSelector:
          matchLabels:
            key: a
          matchExpressions:
            - key: foo
              operator: In
              values:
                - a
                - b
            - key: bar
              operator: NotIn
              values:
                - b
        namespaces:
          - namespace2
        topologyKey: toptop
    """
    logging.debug(f"Parsing weighted pod affinity terms: {items}")
    terms = []
    for item in items:
        terms.append(WeightedPodAffinityTerm(
            weight=item["weight"],
            pod_affinity_term=_parse_pod_affinity_term(item["podAffinityTerm"])
        ))
    if terms: 
        logging.debug(f"Parsed weighted pod affinity terms: {terms}")
    else:
        logging.debug("Couldn't find any weighted pod affinity terms")
    return terms


def _parse_pod_anti_affinity(in_dict: Optional[dict] = None) -> Optional[PodAntiAffinity]:
    """
    Parse PodAntiAffinity.

    podAntiAffinity:
      requiredDuringSchedulingIgnoredDuringExecution:
        ...
      preferredDuringSchedulingIgnoredDuringExecution:
        ...
    """
    logging.debug(f"Parsing pod anti affinity: {in_dict}")
    if in_dict is None:
        logging.debug("Couldn't find pod anti affinity specification, skipping")
        return None
    required_terms = in_dict.get("requiredDuringSchedulingIgnoredDuringExecution", [])
    preferred_terms = in_dict.get("preferredDuringSchedulingIgnoredDuringExecution", [])
    pod_anti_affinity = PodAntiAffinity(
        required_during_scheduling_ignored_during_execution=[_parse_pod_affinity_term(t) for t in required_terms],
        preferred_during_scheduling_ignored_during_execution=_parse_weighted_pod_affinity_terms(preferred_terms),
    )
    logging.debug(f"Parsed pod anti affinity: {pod_anti_affinity}")
    return pod_anti_affinity
