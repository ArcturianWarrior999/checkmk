_TLDR: This README describes the setup steps needed to use azure artifact signing._

# Azure Setup

## Identity and Certificate profile

Follow Azure's [Quickstart](https://learn.microsoft.com/en-us/azure/artifact-signing/quickstart?tabs=registerrp-portal%2Caccount-portal%2Corgvalidation%2Ccertificateprofile-portal%2Cdeleteresources-portal) to perform the setup.
The following pitfalls were experienced on the first setup:

- _Identity validation request_: do not use distribution lists as email adresses, we did not receive mails on them
- _Certificate Profile_: Chose "public trust" - this is the equivalent to the former used "Sectigo OV cert" - avoid private trust
- The first two steps took around one day

## Create an app assigned to the signing account

- Under "Microsoft Entra ID->Manage->Manage" add a new App registration
- Go to the registered app under "Manage->Certificates and Secrets" and create a new secret
- Under "Artifact Signing Accounts->IAM->Add Role assignment" add the above created App

## Usage

In order to sign artifacts the following environment variables must be declared:

```
AZURE_ARTIFACT_SIGNING_ENDPOINT       can be found in the signing account as "Account URI"
AZURE_ARTIFACT_SIGNING_ACCOUNT        the name of the signing account
AZURE_ARTIFACT_SIGNING_PROFILE        Certificate profile name created in the signing account
AZURE_ARTIFACT_SIGNING_TENANT_ID      Azure AD tenant ID
AZURE_ARTIFACT_SIGNING_CLIENT_ID      client ID of the registered app
AZURE_ARTIFACT_SIGNING_CLIENT_SECRET  Service principal client secret (sensitive, the one above created)
```

See `sign_code_azure.ps1` regarding the script to perform the signing.

## View certs

Go to "Artifact Signing Accounts->checkmk->objects->Certificate profiles->CheckmkPublic" and view all existing (active and expired) certificates. At this location a certificate can be revoked.

## Rotate signing secret

By using azure code signing, we do not physically own the private key. The access is solely
established via a secret token.
In order to mitigate the risk, we will use short living secrets and regularly rotate the secret.
This can be done in azure under "Microsoft Entra ID->Manage->App Registration->checkmk-signing->Manage->Certificates & secrets".

When the new secret is created, test it first in the CI by using an intermediate new entry in the credential store and triggering an altered job (see e.g. this [change](https://review.lan.tribe29.com/c/check_mk/+/145660)).
When the new secret works, change the actual secret in Jenkin's credential store and delete the previous token in azure.

## Resources

- [Tutorial](https://hendrik-erz.de/post/code-signing-with-azure-trusted-signing-on-github-actions) for the whole process
