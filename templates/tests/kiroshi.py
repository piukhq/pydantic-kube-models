from starbug.kube.common import Metadata
from starbug.kube.job import Job, JobSpec, JobTemplate, JobTemplateSpec
from starbug.kube.namespace import Namespace
from starbug.kube.pod import Container, ContainerVolume, EnvironmentVariable, ImagePullSecrets, PodVolume
from starbug.kube.serviceaccount import ServiceAccount, ServiceAccountMetadata


class TestComponentKiroshi:
    """Define a Kiroshi Instance."""

    def __init__(self, namespace: Namespace, image: str | None = None) -> None:
        """Initialize the Kiroshi class."""
        self.namespace = namespace
        self.name = "kiroshi-test"
        self.image = "binkcore.azurecr.io/kiroshi-test:latest" if image is None else image
        self.labels = {"app": "kiroshi-test"}
        self.image_pull_secrets = [ImagePullSecrets(name="binkcore.azurecr.io")]
        self.serviceaccount = ServiceAccount(
            metadata=ServiceAccountMetadata(name=self.name, namespace=self.namespace),
        )
        self.test = Job(
            metadata=Metadata(
                labels=self.labels,
                name=self.name,
                namespace=self.namespace,
            ),
            spec=JobSpec(
                template=JobTemplate(
                    spec=JobTemplateSpec(
                        containers=[
                            Container(
                                name="app",
                                image=self.image,
                                volume_mounts=[
                                    ContainerVolume(),
                                ],
                            ),
                            Container(
                                name="azcopy",
                                image="ghcr.io/binkhq/oci-azcopy:latest",
                                command=["linkerd-await", "--shutdown", "--"],
                                args=[
                                    "bash",
                                    "-c",
                                    'until [ -f ${REPORT_DIRECTORY}/${REPORT_FILE} ]; do sleep 5; done; sleep 5; azcopy copy "${REPORT_DIRECTORY}/${REPORT_FILE}" "${STORAGE_URL}/${STORAGE_CONTAINER}/$(cat ${NAMESPACE_FILE})/${REPORT_FILE}?${STORAGE_QUERY_STRING}"'],  # noqa: E501
                                env=[
                                    EnvironmentVariable(
                                        name="REPORT_DIRECTORY",
                                        value="/mnt/reports",
                                    ),
                                    EnvironmentVariable(
                                        name="REPORT_FILE",
                                        value="report.json",
                                    ),
                                    EnvironmentVariable(
                                        name="NAMESPACE_FILE",
                                        value="/var/run/secrets/kubernetes.io/serviceaccount/namespace",
                                    ),
                                    EnvironmentVariable(
                                        name="STORAGE_URL",
                                        value="https://uksouthait20kg.blob.core.windows.net",
                                    ),
                                    EnvironmentVariable(
                                        name="STORAGE_CONTAINER",
                                        value="starbug-reports",
                                    ),
                                    EnvironmentVariable(
                                        name="STORAGE_QUERY_STRING",
                                        value="sv=2021-10-04&st=2023-08-21T14%3A38%3A32Z&se=2030-01-01T00%3A00%3A00Z&sr=c&sp=racwl&sig=R%2Buqs%2F61BtR5g5pa%2Fu31E8g%2BmuZ7P5EepyA%2FG6QZEcM%3D",
                                    ),
                                ],
                                volume_mounts=[
                                    ContainerVolume(),
                                ],
                            ),
                        ],
                        volumes=[
                            PodVolume(),
                        ],
                        image_pull_secrets=self.image_pull_secrets,
                        service_account_name=self.serviceaccount.metadata.name,
                    ),
                ),
            ),
        )

    def __iter__(self) -> list:
        """Return all Objects as a list."""
        yield from [self.serviceaccount, self.test]
