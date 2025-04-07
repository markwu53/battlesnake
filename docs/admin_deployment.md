# Admin Deployment

<!-- TOC -->

* [Admin Deployment](#admin-deployment)
    * [Create a GitLab Repository](#create-a-gitlab-repository)
    * [Create a Railway Project](#create-a-railway-project)
    * [Create GitLab CI/CD Variables](#create-gitlab-cicd-variables)
    * [Validate Deployment](#validate-deployment)
    * [Add Participant to Railway Project](#add-participant-to-railway-project)

<!-- TOC -->

## Create a GitLab Repository

An administrator with sufficient permissions to create and configure a GitLab repo will need to perform the following
steps:

1. Navigate to the [training/battlesnakes group](https://git.mmi.mig.corp/training/battlesnakes)
2. Select "New Project"

   <img src="assets/admin_deployment/01_new_project.png" alt="New GitLab Project" height="200">
3. Select "Create from template"

   <img src="assets/admin_deployment/02_create_from_template.png" alt="New GitLab Project" height="200">
4. Select "Group" to access group-specific templates

   <img src="assets/admin_deployment/03_create_from_template_2.png" alt="New GitLab Project" height="200">
5. Select `Use template` next to the `battlesnakes` template

   <img src="assets/admin_deployment/04_create_from_template_3.png" alt="New GitLab Project" height="200">
6. Begin the project name with the participant's T-number. You can follow it with their snake's name.

   <img src="assets/admin_deployment/05_create_project.png" alt="New GitLab Project" height="400">

## Create a Railway Project

We're going to create a Railway project and gather two variables that we will use to configure the GitLab repo.

1. Login to [Railway](https://railway.com/) and create a new project in a shared workspace with billing configured. If
   you deploy a project to your personal space, you will eventually need to supply billing information. Additionally,
   you won't be able to invite other team members.

   <img src="assets/admin_deployment/10_create_new_railway_project.png" alt="New GitLab Project" height="200">
2. Select "Empty Project"

   <img src="assets/admin_deployment/11_create_new_railway_project_2.png" alt="New GitLab Project" height="400">
3. Select "Settings" in the upper right-hand side of the screen.

   <img src="assets/admin_deployment/12_rename_railway_project_1.png" alt="New GitLab Project" height="500">
4. Rename the project to the participant's T-number followed by their name (e.g. `T905376 Zane Clark`). Select `Update`
   to apply the changes

   <img src="assets/admin_deployment/13_rename_railway_project_2.png" alt="New GitLab Project" height="400">
5. Select `Tokens` from the menu on the left of the screen.

   <img src="assets/admin_deployment/14_rename_railway_project_3.png" alt="New GitLab Project" height="400">
6. Supply a token name (e.g. `GITLAB_DEPLOY`) and create a new token.

   <img src="assets/admin_deployment/16_create_token_2.png" alt="New GitLab Project" height="350">
7. **Save the token value.** You won't be able to see it again when you move away from this screen. We will use it in a
   few steps. Press the "x" on the upper right-hand side of the screen to close `Project Settings`.

   <img src="assets/admin_deployment/17_create_token_3.png" alt="New GitLab Project" height="370">
8. Click on the `Add a service` prompt.

   <img src="assets/admin_deployment/18_create_service_1.png" alt="New GitLab Project" height="370">
9. Select `Empty Service`

   <img src="assets/admin_deployment/19_create_service_2.png" alt="New GitLab Project" height="300">
10. Right-click on the service you just created.

    <img src="assets/admin_deployment/20_create_service_3.png" alt="New GitLab Project" height="370">
11. Select `Update info` > `Name`. Change the name of the service to match the name of the snake from the GitLab repo. *
    *Note: The service name cannot contain any spaces.**

    <img src="assets/admin_deployment/21_rename_service_1.png" alt="New GitLab Project" height="370">
12. Click on the renamed service.

    <img src="assets/admin_deployment/22_get_service_name_1.png" alt="New GitLab Project" height="370">
13. Select `Variables` from the service menu.

    <img src="assets/admin_deployment/23_get_service_name_2.png" alt="New GitLab Project" height="400">
14. Expand the chevron to the left of `Railway Provided Variables`.

    <img src="assets/admin_deployment/24_get_service_name_3.png" alt="New GitLab Project" height="400">
15. Copy the value for `RAILWAY_SERVICE_NAME`. Press the "x" on the upper right-hand side of the screen to close
    `Service Settings`.

    <img src="assets/admin_deployment/25_get_service_name_4.png" alt="New GitLab Project" height="400">
16. Back on the dashboard, select `Deploy` to apply your changes.

    <img src="assets/admin_deployment/27_save_changes.png" alt="New GitLab Project" height="400">

## Create GitLab CI/CD Variables

Next, we'll create GitLab CI/CD variables with the token and `RAILWAY_SERVICE_NAME` values that we sourced from Railway.

1. Navigate back to the GitLab repository and select `Settings` > `CI/CD`.

   <img src="assets/admin_deployment/30_set_cicd_variables_1.png" alt="New GitLab Project" height="500">
2. Select `Variables` to expand the category.

   <img src="assets/admin_deployment/31_set_cicd_variables_2.png" alt="New GitLab Project" height="400">
3. Select `Add variable` to add a new CI/CD variable that is specific to this repository.

   <img src="assets/admin_deployment/32_set_cicd_variables_3.png" alt="New GitLab Project" height="400">
4. Create a variable:
    - **Visibility**: Visible
    - **Key**: `RAILWAY_SERVICE_NAME`
    - **Value**: The value that we extracted from Railway

   Select `Add variable` to save it.

      <img src="assets/admin_deployment/33_set_cicd_variables_4.png" alt="New GitLab Project" height="500">
5. Create a variable:
    - **Visibility**: Masked
    - **Key**: `RAILWAY_TOKEN`
    - **Value**: The token value that we extracted from Railway

   Select `Add variable` to save it.

   <img src="assets/admin_deployment/34_set_cicd_variables_5.png" alt="New GitLab Project" height="500">
6. You should now see two CI/CD Variables for the project:

   <img src="assets/admin_deployment/35_set_cicd_variables_6.png" alt="New GitLab Project" height="400">

## Validate Deployment

Now, we will execute the GitLab CI/CD pipeline to validate the configuration.

1. Using the menu on the left of the screen, navigate to `Build` > `Pipelines`.

   <img src="assets/admin_deployment/40_deploy_1.png" alt="New GitLab Project" height="500">
2. Select `New pipeline` to kick off a new pipeline

   <img src="assets/admin_deployment/41_deploy_2.png" alt="New GitLab Project" height="200">
3. Select `Run pipeline` to accept the default branch target of `master`

   <img src="assets/admin_deployment/42_deploy_3.png" alt="New GitLab Project" height="250">
4. Two tasks will run. First, the runner will install the requirements in the repo using `pdm` and execute `pytest`.
   Second, the runner will use the Railway token and service name to deploy the repo to the Railway service that we
   created earlier.

   <img src="assets/admin_deployment/43_deploy_4.png" alt="New GitLab Project" height="300">
5. To view the progress and logs, navigate back to the Railway project and select the service. The default `Deployments`
   tab can be used to view the `build` and `deploy` logs.

   <img src="assets/admin_deployment/46_deploy_7.png" alt="New GitLab Project" height="350">
6. Wait for the deployment to succeed to move to the next step.

   <img src="assets/admin_deployment/45_deploy_6.png" alt="New GitLab Project" height="300">

## Add Participant to Railway Project

1. Navigate back to the Railway project

   <img src="assets/admin_deployment/70_add_participant_1.png" alt="New GitLab Project" height="400">

2. Select `Members` on the left menu. Invite the member with `Can Edit` permissions.

   <img src="assets/admin_deployment/71_add_participant_2.png" alt="New GitLab Project" height="400">

3. The participant will create a free Railway account and accept the invitation.

   <img src="assets/admin_deployment/72_add_participant_3.png" alt="New GitLab Project" height="400">

4. When that's done, the invitation will no longer show as pending.

   <img src="assets/admin_deployment/73_add_participant_4.png" alt="New GitLab Project" height="400">
