"""Postgres Application Kubernetes Objects."""

from starbug.kube.deployment import simple_deployment
from starbug.kube.pod import EnvironmentVariable
from starbug.kube.service import Service, ServiceMetadata, ServicePort, ServiceSpec
from starbug.kube.serviceaccount import ServiceAccount, ServiceAccountMetadata


class Postgres:
    """Defines a Postgres Instance."""

    def __init__(self, namespace: str, image: str | None = None) -> None:
        """Initialize the Postgres Class."""
        self.namespace = namespace
        self.name = "postgres"
        self.image = "docker.io/postgres:14" if image is None else image
        self.labels = {"app": "postgres"}
        self.serviceaccount = ServiceAccount(
            metadata=ServiceAccountMetadata(name=self.name, namespace=self.namespace),
        )
        self.service = Service(
            metadata=ServiceMetadata(name=self.name, namespace=self.namespace, labels=self.labels),
            spec=ServiceSpec(ports=[ServicePort(port=5432, target_port=5432)], selector=self.labels),
        )
        self.deployment = simple_deployment(
            name=self.name,
            namespace=self.namespace,
            labels=self.labels,
            image=self.image,
            environment_variables=[EnvironmentVariable(name="POSTGRES_HOST_AUTH_METHOD", value="trust")],
            service_account=self.serviceaccount.metadata.name,
        )

    def __iter__(self) -> list:
        """Return all Objects as a list."""
        yield from [self.serviceaccount, self.service, self.deployment]
