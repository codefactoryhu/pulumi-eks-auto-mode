import pulumi
from pulumi import Output
import pulumi_aws as aws


class KMS:
    """Manages AWS KMS keys and aliases for various infrastructure components"""
    
    def __init__(
        self,
        name: str,
        description: str,
        purpose: str,
        deletion_window_in_days: int = 7,
    ):
        """
        Create a new KMS key with alias
        
        Args:
            name: Name identifier for the KMS key 
            description: Description of the key's purpose
            purpose: Short tag value describing the key's usage
            deletion_window_in_days: Waiting period before key deletion (7-30 days)
        """
        self._name = name
        self._purpose = purpose
        self._description = description
        self._deletion_window_in_days = max(7, min(deletion_window_in_days, 30))  # Enforce valid range

        self._key = self._create_kms_key()
        self._alias = self._create_kms_alias()

        self._export_key_arn()

    def _create_kms_key(self) -> aws.kms.Key:
        """Create the KMS key with specified configuration"""
        return aws.kms.Key(
            f"{self._name}-key",
            description=self._description,
            deletion_window_in_days=self._deletion_window_in_days,
            enable_key_rotation=True,
            tags={
                "Name": self._name, 
                "Purpose": self._purpose,
                "ManagedBy": "Pulumi"
            },
        )

    def _create_kms_alias(self) -> aws.kms.Alias:
        """Create an alias for the KMS key"""
        return aws.kms.Alias(
            f"{self._name}-alias",
            name=f"alias/{self._name}",
            target_key_id=self._key.id,
        )

    def _export_key_arn(self) -> None:
        """Export the KMS key ARN as a Pulumi stack output"""
        pulumi.export(f"{self._name}_kms_key_arn", self._key.arn)

    def get_key_arn(self) -> Output[str]:
        """
        Returns the ARN of the KMS key
        
        Returns:
            Pulumi output containing the KMS key ARN
        """
        return self._key.arn
    
    def get_key_id(self) -> Output[str]:
        """
        Returns the ID of the KMS key
        
        Returns:
            Pulumi output containing the KMS key ID
        """
        return self._key.id