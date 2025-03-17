# Git Workflow Documentation

## Branch Structure

- **main**: Production branch. Code in this branch is deployed to the production environment.
- **staging**: Pre-production branch. Code in this branch is deployed to the staging environment for testing.
- **feature/\***: Feature branches for new development.
- **bugfix/\***: Branches for bug fixes.

## Workflow Rules

### 1. Creating a New Feature or Bug Fix

Always create your branch from the latest version of `staging`:

```bash
git checkout staging
git pull origin staging
git checkout -b feature/FEATURE-NAME
# or for bug fixes
git checkout -b bugfix/BUG-NAME
```

### 2. Developing Your Feature

Commit your changes regularly with descriptive commit messages:

```bash
git add .
git commit -m "Descriptive message about your changes"
```

Keep your branch up to date with staging:

```bash
git checkout staging
git pull origin staging
git checkout feature/FEATURE-NAME
git merge staging  # Resolve any conflicts that may arise
```

### 3. Creating a Pull Request to Staging

When your feature is complete:

1. Push your branch to GitHub:
   ```bash
   git push -u origin feature/FEATURE-NAME
   ```

2. Go to GitHub and create a Pull Request to merge your branch into `staging`.
3. Assign reviewers and wait for approval.
4. Once approved, merge the PR into `staging`.
5. The code will automatically be deployed to the staging environment for testing.

### 4. Promoting to Production

After testing in the staging environment:

1. Go to GitHub and create a Pull Request to merge `staging` into `main`.
2. **IMPORTANT**: Only PRs from `staging` to `main` will be accepted. PRs from feature branches directly to `main` will be automatically rejected.
3. Assign reviewers and wait for approval.
4. Once approved, merge the PR into `main`.
5. The code will automatically be deployed to the production environment.

## Hotfixes

For critical production issues that need immediate fixes:

1. Create a hotfix branch from `main`:
   ```bash
   git checkout main
   git pull origin main
   git checkout -b hotfix/HOTFIX-NAME
   ```

2. Make the necessary changes and push to GitHub.
3. Create a PR to merge the hotfix into `main`.
4. After the hotfix is merged into `main`, create another PR to merge the changes back into `staging` to keep the branches in sync.

## CI/CD Pipelines

- All PRs to `staging` and `main` trigger automated tests.
- Merges to `staging` trigger deployment to the staging environment.
- Merges to `main` trigger deployment to the production environment.

## Best Practices

1. Keep your commits small and focused on a single task.
2. Write descriptive commit messages.
3. Regularly pull changes from `staging` to your feature branch.
4. Always test your changes in the staging environment before promoting to production.
5. Communicate with the team when merging significant changes.
6. Delete feature branches after they are merged. 