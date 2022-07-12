import logging

from django.db.models import Q
from django.db.models.signals import post_save
from django.dispatch import receiver

from audit.decorators import handle_skipped_signals
from audit.models import AuditLog, RelatedObjectType
from audit.serializers import AuditLogSerializer
from environments.models import Environment
from integrations.datadog.datadog import DataDogWrapper
from integrations.dynatrace.dynatrace import DynatraceWrapper
from integrations.new_relic.new_relic import NewRelicWrapper
from integrations.slack.slack import SlackWrapper
from webhooks.webhooks import WebhookEventType, call_organisation_webhooks

logger = logging.getLogger(__name__)


@receiver(post_save, sender=AuditLog)
@handle_skipped_signals
def call_webhooks(sender, instance, **kwargs):
    data = AuditLogSerializer(instance=instance).data

    if not (instance.project or instance.environment):
        logger.warning("Audit log without project or environment. Not sending webhook.")
        return

    organisation = (
        instance.project.organisation
        if instance.project
        else instance.environment.project.organisation
    )
    call_organisation_webhooks(organisation, data, WebhookEventType.AUDIT_LOG_CREATED)


def _get_integration_config(instance, integration_name):
    if hasattr(instance.project, integration_name):
        return getattr(instance.project, integration_name)
    elif hasattr(instance.environment, integration_name):
        return getattr(instance.environment, integration_name)

    return None


def track_only_feature_related_events(signal_function):
    def signal_wrapper(sender, instance, **kwargs):
        # Only handle Feature related changes
        if instance.related_object_type not in [
            RelatedObjectType.FEATURE.name,
            RelatedObjectType.FEATURE_STATE.name,
            RelatedObjectType.SEGMENT.name,
        ]:
            return None
        return signal_function(sender, instance, **kwargs)

    return signal_wrapper


def _track_event_async(instance, integration_client):
    event_data = integration_client.generate_event_data(
        log=instance.log,
        email=instance.author.email if instance.author else "",
        environment_name=instance.environment.name.lower()
        if instance.environment
        else "",
    )

    integration_client.track_event_async(event=event_data)


@receiver(post_save, sender=AuditLog)
@track_only_feature_related_events
@handle_skipped_signals
def send_audit_log_event_to_datadog(sender, instance, **kwargs):
    data_dog_config = _get_integration_config(instance, "data_dog_config")

    if not data_dog_config:
        return

    data_dog = DataDogWrapper(
        base_url=data_dog_config.base_url, api_key=data_dog_config.api_key
    )
    _track_event_async(instance, data_dog)


@receiver(post_save, sender=AuditLog)
@track_only_feature_related_events
@handle_skipped_signals
def send_audit_log_event_to_new_relic(sender, instance, **kwargs):

    new_relic_config = _get_integration_config(instance, "new_relic_config")
    if not new_relic_config:
        return

    new_relic = NewRelicWrapper(
        base_url=new_relic_config.base_url,
        api_key=new_relic_config.api_key,
        app_id=new_relic_config.app_id,
    )
    _track_event_async(instance, new_relic)


@receiver(post_save, sender=AuditLog)
@track_only_feature_related_events
@handle_skipped_signals
def send_audit_log_event_to_dynatrace(sender, instance, **kwargs):

    dynatrace_config = _get_integration_config(instance, "dynatrace_config")
    if not dynatrace_config:
        return

    dynatrace = DynatraceWrapper(
        base_url=dynatrace_config.base_url,
        api_key=dynatrace_config.api_key,
        entity_selector=dynatrace_config.entity_selector,
    )
    _track_event_async(instance, dynatrace)


@receiver(post_save, sender=AuditLog)
@handle_skipped_signals
def send_environments_to_dynamodb(sender, instance, **kwargs):
    environments_filter = (
        Q(id=instance.environment_id)
        if instance.environment_id
        else Q(project=instance.project)
    )
    Environment.write_environments_to_dynamodb(environments_filter)


@receiver(post_save, sender=AuditLog)
@track_only_feature_related_events
@handle_skipped_signals
def send_audit_log_event_to_slack(sender, instance, **kwargs):
    slack_project_config = _get_integration_config(instance, "slack_config")
    if not slack_project_config:
        return
    env_config = slack_project_config.env_config.filter(
        environment=instance.environment, enabled=True
    ).first()
    if not env_config:
        return
    slack = SlackWrapper(
        api_token=slack_project_config.api_token, channel_id=env_config.channel_id
    )
    _track_event_async(instance, slack)
