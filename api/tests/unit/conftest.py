import pytest
from rest_framework.test import APIClient

from api_keys.models import MasterAPIKey
from environments.models import Environment
from features.models import Feature
from organisations.models import Organisation, OrganisationRole
from projects.models import Project
from users.models import FFAdminUser


@pytest.fixture()
def organisation_one(db):
    return Organisation.objects.create(name="Test organisation 1")


@pytest.fixture()
def organisation_two(db):
    return Organisation.objects.create(name="Test organisation 2")


@pytest.fixture()
def organisation_one_project_one(organisation_one):
    return Project.objects.create(name="Test Project 1", organisation=organisation_one)


@pytest.fixture()
def organisation_one_project_two(organisation_one):
    return Project.objects.create(name="Test Project 2", organisation=organisation_one)


@pytest.fixture()
def organisation_two_project_one(organisation_two):
    return Project.objects.create(name="Test Project 1", organisation=organisation_two)


@pytest.fixture()
def organisation_two_project_two(organisation_two):
    return Project.objects.create(name="Test Project 2", organisation=organisation_two)


@pytest.fixture()
def organisation_one_project_one_environment_one(organisation_one_project_one):
    return Environment.objects.create(
        name="Test Environment 1", project=organisation_one_project_one
    )


@pytest.fixture()
def organisation_one_project_one_environment_two(organisation_one_project_one):
    return Environment.objects.create(
        name="Test Environment 2", project=organisation_one_project_one
    )


@pytest.fixture()
def organisation_two_project_one_environment_one(organisation_two_project_one):
    return Environment.objects.create(
        name="Test Environment 1", project=organisation_two_project_one
    )


@pytest.fixture()
def organisation_two_project_one_environment_two(organisation_two_project_one):
    return Environment.objects.create(
        name="Test Environment 2", project=organisation_two_project_one
    )


@pytest.fixture()
def user_one():
    return FFAdminUser.objects.create(email="test@example.com")


@pytest.fixture()
def organisation_one_user(user_one, organisation_one):
    user_one.add_organisation(organisation_one)
    return user_one


@pytest.fixture()
def organisation_one_admin_user(organisation_one):
    organisation_one_admin_user = FFAdminUser.objects.create(
        email="org1_admin@example.com"
    )
    organisation_one_admin_user.add_organisation(
        organisation_one, role=OrganisationRole.ADMIN
    )
    return organisation_one_admin_user


@pytest.fixture()
def organisation_one_project_one_feature_one(organisation_one_project_one):
    return Feature.objects.create(
        project=organisation_one_project_one,
        name="feature_1",
        initial_value="feature_1_value",
    )


@pytest.fixture()
def master_api_key(organisation):
    _, key = MasterAPIKey.objects.create_key(name="test_key", organisation=organisation)
    return key


@pytest.fixture()
def master_api_key_client(master_api_key):
    # Can not use `api_client` fixture here because:
    # https://docs.pytest.org/en/6.2.x/fixture.html#fixtures-can-be-requested-more-than-once-per-test-return-values-are-cached
    api_client = APIClient()
    api_client.credentials(HTTP_AUTHORIZATION="Api-Key " + master_api_key)
    return api_client


@pytest.fixture()
def dynamo_enabled_project(organisation_one):
    return Project.objects.create(
        name="Dynamo enabled project",
        organisation=organisation_one,
        enable_dynamo_db=True,
    )


@pytest.fixture()
def dynamo_enabled_project_environment_one(dynamo_enabled_project):
    return Environment.objects.create(
        name="Env 1", project=dynamo_enabled_project, api_key="env-1-key"
    )


@pytest.fixture()
def dynamo_enabled_project_environment_two(dynamo_enabled_project):
    return Environment.objects.create(
        name="Env 2", project=dynamo_enabled_project, api_key="env-2-key"
    )
