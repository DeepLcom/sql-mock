# Contributing Code

If you're interested in contributing code, follow these steps:

1. **Fork the Repository**: Fork the project's repository to your GitHub account.

2. **Create a Branch**: Create a new branch for your contribution, preferably with a name that describes the feature or fix you're working on.

3. **Code and Test**: Write your code, and make sure to test it thoroughly to ensure it functions as expected.

4. **Documentation**: If your contribution involves code changes, update the relevant documentation to reflect those changes.

5. **Submit a Pull Request**: Submit a pull request to the project's repository. Be sure to provide a clear and concise description of your changes. Include a reference to any related issues.

6. **Code Review**: Your pull request will undergo code review by maintainers and contributors. Be prepared to address any feedback and make necessary changes.

7. **Merge**: Once your contribution is approved and passes all checks, it will be merged into the project.

## Coding Standards

When contributing code, adhere to the following coding standards:

- Follow the project's coding style, including code formatting and naming conventions.
- Ensure your code is well-documented and includes comments where necessary.
- Write clear commit messages that describe the purpose of each commit.

## Local Setup

To set up your local development environment for this project, follow these steps:

### 1. Clone the Repository

```bash
git clone https://github.com/your-project/repository.git
cd repository
```

### 2. Install Dependencies

We use [Poetry](https://python-poetry.org/) for dependency management. If you don't have Poetry installed, you can get it from [here](https://python-poetry.org/docs/#installation).

Once you have Poetry, you can install the project's dependencies:

```bash
poetry install --all-extras
```

### 3. Pre-Commit Hooks

This project uses pre-commit hooks to ensure code quality. To install the hooks, run:

```bash
poetry run pre-commit install
```

This will set up the necessary hooks to check code formatting, linting, and other code quality checks before each commit.

### 4. Running Tests

We use [pytest](https://docs.pytest.org/en/latest/) for running tests. You can run all the tests with:

```bash
poetry run pytest tests/
```

### 5. Environment Variables

If you're working with database-specific sections (e.g., BigQuery or ClickHouse), make sure to set the required environment variables for your chosen database. Refer to the respective "Usage" sections for details on these variables.

### 6. Development Workflow

Before you start contributing, create a new branch for your work:

```bash
git checkout -b your-feature-branch
```

Make your code changes, commit them, and create a pull request to the project's repository following the [Contributing Guidelines](#Contributing).

### 7. Code Formatting and Linting

As part of the pre-commit hooks, code formatting and linting will be automatically checked before each commit. Be sure to address any issues reported by the hooks.

### 8. Update documentation

We are using sphinx to generate our documentation. 
The documentation pages can be found in `docsource`. Go there and add / adjust the files.
After that, we need to run `make build-docs-github` in order to populate the changes in the documentation and commit those.


## Release process

To create a new release, you need to perform the following steps:

1. Create a PR to bump the library version, update the changelog, etc. The full steps needed can be found in the [PR template for a release process](https://github.com/DeepLcom/sql-mock/blob/a98eca804e0901b8b4488f8ed95e0bff32cf112b/.github/PULL_REQUEST_TEMPLATE/release_template.md?plain=1).
2. Merge your PR
3. Go to [Releaes](https://github.com/DeepLcom/sql-mock/releases) and [draft a new release](https://github.com/DeepLcom/sql-mock/releases/new). You might need to create a new Tag with the same version as the updated one from your PR. Make sure to describe the changes made (compare to previous releases). You can copy-paste the content for your new version from the changelog. Select the latest master branch as a target branch.
4. When your release is published, an automatic GitHub action should take care of publishing the release to PyPi. Monitor the [actions](https://github.com/DeepLcom/sql-mock/actions) to check that everything works.
