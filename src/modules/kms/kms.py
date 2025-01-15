import pulumi
import pulumi_aws as aws


class KMS:
    def __init__(
        self,
        name: str,
        description: str,
        purpose: str,
        deletion_window_in_days: int = 7,
    ):
        self._name = name
        self._purpose = purpose
        self._description = description
        self._deletion_window_in_days = deletion_window_in_days

        self._key = self._create_kms_key()
        self._alias = self._create_kms_alias()

        self._export_key_arn()

    def _create_kms_key(self):
        return aws.kms.Key(
            f"{self._name}-key",
            description=self._description,
            deletion_window_in_days=self._deletion_window_in_days,
            enable_key_rotation=True,
            tags={"Name": self._name, "Purpose": self._purpose},
        )

    def _create_kms_alias(self):
        return aws.kms.Alias(
            f"{self._name}-alias",
            name=f"alias/{self._name}",
            target_key_id=self._key.id,
        )

    def _export_key_arn(self):
        pulumi.export(f"{self._name}_kms_key_arn", self._key.arn)

    def get_key_arn(self):
        return self._key.arn
