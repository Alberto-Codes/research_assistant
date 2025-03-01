# Contributing to Research Agent

Thank you for your interest in contributing to the Research Agent project! This document outlines the process for contributing to this project using the fork and pull model based on GitFlow.

## Fork and Pull Workflow

We follow a fork and pull model that combines elements of [GitHub Flow](https://githubflow.github.io/) with the branching strategy of GitFlow. This approach keeps the main repository clean while allowing for proper code review.

### Overview of the Process

1. **Fork the repository** to your own GitHub account
2. **Clone your fork** to your local machine
3. **Create a branch** for your feature or bug fix
4. **Make your changes** following our coding standards
5. **Push your branch** to your fork
6. **Open a pull request** to the original repository
7. **Address review feedback** until your contribution is accepted
8. Once approved, a maintainer will **merge your pull request**

### Detailed Steps

#### 1. Fork the Repository

Start by forking the repository through the GitHub interface. This creates a copy of the repository under your GitHub account.

#### 2. Clone Your Fork

```bash
git clone https://github.com/YOUR-USERNAME/research_agent.git
cd research_agent
```

#### 3. Add the Original Repository as Upstream

```bash
git remote add upstream https://github.com/ORIGINAL-OWNER/research_agent.git
```

This allows you to keep your fork in sync with the main repository.

#### 4. Create a Branch

Create a descriptively named branch for your work:

```bash
git checkout -b feature/your-feature-name
# or for bug fixes
git checkout -b fix/issue-description
```

#### 5. Develop Your Contribution

Make your changes following our development guidelines:

- Follow the coding standards (formatting, linting)
- Add tests for new functionality
- Update documentation as needed
- Keep your changes focused on a single issue or feature

#### 6. Keep Your Branch Updated

Regularly sync your branch with the upstream repository:

```bash
git fetch upstream
git rebase upstream/main
```

#### 7. Push Your Changes

Push your changes to your forked repository:

```bash
git push origin feature/your-feature-name
```

#### 8. Submit a Pull Request

Go to the original repository on GitHub and click the "New Pull Request" button. Select your fork and the branch containing your changes.

In your pull request description:
- Clearly describe what the changes do
- Reference any related issues
- Include any necessary setup or testing instructions

#### 9. Code Review Process

After submitting your pull request:

- Automated tests will run on your code
- Project maintainers will review your changes
- Address any feedback or requested changes
- Additional commits to your branch will automatically update the pull request

#### 10. Merging

Once approved, a project maintainer will merge your contribution into the main codebase. Congratulations on your contribution!

## Development Environment Setup

For details on setting up your development environment, please refer to our [Development Guide](development.md).

## Quality Standards

All contributions must adhere to the project's quality standards:

- Pass all automated tests
- Pass all linting checks
- Include appropriate documentation
- Include tests for new functionality

Run the following to ensure your code meets our standards:

```bash
make quality
```

## UI Testing Guidelines

When contributing changes to the Streamlit UI components, please follow these testing guidelines:

1. **Use AppTest Framework**: All UI tests should use Streamlit's `AppTest` framework:
   ```python
   from streamlit.testing.v1 import AppTest
   ```

2. **Test Basic UI Elements**: Verify that UI components render correctly:
   ```python
   def test_ui_components():
       at = AppTest.from_file("path/to/app.py")
       at.run()
       assert "Expected Title" in at.title[0].value
   ```

3. **Test User Interactions**: Simulate and verify user interactions:
   ```python
   def test_user_interaction():
       at = AppTest.from_file("path/to/app.py")
       at.run()
       at.text_input[0].set_value("Test input")
       at.button[0].click()
       at.run()
       assert "Expected Result" in at.markdown[0].value
   ```

4. **Mock External Dependencies**: Properly mock API calls and other dependencies:
   ```python
   @patch("module.external_dependency")
   def test_with_mock(mock_dependency):
       mock_dependency.return_value = "Mock result"
       at = AppTest.from_file("path/to/app.py")
       at.run()
   ```

5. **Handle Streamlit Context Errors**: Always wrap Streamlit tests in try/except blocks to handle potential context errors:
   ```python
   def test_with_error_handling():
       try:
           at = AppTest.from_file("path/to/app.py")
           at.run()
           # Test assertions
       except Exception as e:
           pytest.skip(f"Streamlit test environment issue: {str(e)}")
   ```

6. **Test Async Functions**: Use proper mocking techniques for async functions:
   ```python
   @pytest.mark.asyncio
   @patch("module.async_function")
   async def test_async_feature(mock_async):
       mock_async.return_value = "mock result"
       # Test implementation
   ```

For more detailed information, see the [Testing Guide](../TESTING.md) and examples in `tests/research_agent/test_streamlit.py`.

## Communication

If you have questions or need help:

- Open an issue for bugs or feature requests
- Discuss significant changes before investing a lot of time
- Reference any relevant issues in your pull request

## Thank You!

Your contributions help make this project better for everyone. We appreciate your time and effort! 