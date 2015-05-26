from .bases import SecretBackend
from aiovault.exceptions import InvalidPath
from aiovault.objects import Value
from aiovault.util import task


class AWSBackend(SecretBackend):
    """
    The AWS backend dynamically generates AWS access keys for a set of
    IAM policies. The AWS access keys have a configurable lease set and
    are automatically revoked at the end of the lease.

    After mounting this backend, credentials to generate IAM keys must
    be configured with the "root" path and policies must be written using
    the "roles/" endpoints before any access keys can be generated.
    """

    def __init__(self, name, req_handler):
        self.name = name
        self.req_handler = req_handler

    @task
    def config_root(self, *, access_key, secret_key, region=None):
        """Configures the root IAM credentials used.

        Before doing anything, the AWS backend needs credentials that are able
        to manage IAM policies, users, access keys, etc. This endpoint is used
        to configure those credentials. They don't necessarilly need to be root
        keys as long as they have permission to manage IAM::

            {
                "Version": "2012-10-17",
                "Statement": [
                    {
                        "Sid": "Stmt1432042359000",
                        "Effect": "Allow",
                        "Action": [
                            "iam:CreateUser",
                            "iam:PutUserPolicy",
                            "iam:CreateAccessKey"
                        ],
                        "Resource": [
                            "*"
                        ]
                    }
                ]
            }

        Parameters:
            access_key (str): Access key with permission to create new keys
            secret_key (str): Secret key with permission to create new keys
            region (str): The region for API calls
        Returns:
            bool
        """
        method = 'POST'
        path = '/%s/config/root' % self.name
        data = {'access_key': access_key,
                'secret_key': secret_key,
                'region': region}

        response = yield from self.req_handler(method, path, json=data)
        return response.status == 204

    @task
    def config_lease(self, *, lease, lease_max):
        """Configures the lease settings for generated credentials.

        This configures the default lease information used for credentials
        generated by this backend. The lease specifies the duration that a
        credential will be valid for, as well as the maximum session for
        a set of credentials.

        The format for the lease is "1h" or integer and then unit. The longest
        unit is hour.

        Parameters:
            lease (str): The lease value provided as a string duration with
                         time suffix. Hour is the largest suffix.
            lease_max (str): The maximum lease value provided as a string
                             duration with time suffix. Hour is the largest
                             suffix.
        Returns:
            bool
        """
        method = 'POST'
        path = '/%s/config/lease' % self.name
        data = {'lease': lease,
                'lease_max': lease_max}

        response = yield from self.req_handler(method, path, json=data)
        return response.status == 204

    @task
    def write_role(self, name, *, policy):
        """Write named role.

        This path allows you to read and write roles that are used to create
        access keys. These roles have IAM policies that map directly to the
        route to read the access keys. For example, if the backend is mounted
        at "aws" and you create a role at "aws/roles/deploy" then a user could
        request access credentials at "aws/creds/deploy".

        The policies written are normal IAM policies. Vault will not attempt to
        parse these except to validate that they're basic JSON. To validate the
        keys, attempt to read an access key after writing the policy.

        Parameters:
            name (str): The role name.
            policy (obj): The IAM policy.
        Returns:
            bool
        """
        method = 'POST'
        path = '/%s/roles/%s' % (self.name, name)
        data = {'policy': policy}

        response = yield from self.req_handler(method, path, json=data)
        return response.status == 204

    @task
    def read_role(self, name):
        """Read a named role.

        Parameters:
            name (str): The role name.
        Returns:
            Value
        """
        method = 'GET'
        path = '/%s/roles/%s' % (self.name, name)

        try:
            response = yield from self.req_handler(method, path)
            result = yield from response.json()
            return Value(**result)
        except InvalidPath:
            raise KeyError('%r does not exists' % name)

    @task
    def delete_role(self, name):
        """Delete a named role.

        Parameters:
            name (str): The role name.
        Returns:
            bool
        """
        method = 'DELETE'
        path = '/%s/roles/%s' % (self.name, name)

        response = yield from self.req_handler(method, path)
        return response.status == 204

    @task
    def creds(self, name):
        """Generates a dynamic IAM credential based on the named role.

        Parameters:
            name (str): The role name.
        Returns:
            Value
        """
        method = 'GET'
        path = '/%s/creds/%s' % (self.name, name)

        response = yield from self.req_handler(method, path)
        result = yield from response.json()
        return Value(**result)
