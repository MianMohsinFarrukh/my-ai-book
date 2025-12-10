# Deployment Instructions: Physical AI & Robotics Textbook

## GitHub Pages Deployment

### Prerequisites
- Git repository initialized and connected to GitHub
- GitHub Actions enabled for the repository
- Repository settings configured for GitHub Pages

### Deployment Steps

1. **Prepare the repository**:
   ```bash
   # Ensure all changes are committed
   git add .
   git commit -m "Prepare for GitHub Pages deployment"
   git push origin main
   ```

2. **Configure GitHub Pages**:
   - Go to your repository on GitHub
   - Navigate to Settings > Pages
   - Under "Build and deployment", select "GitHub Actions" as the source
   - GitHub Actions workflow is already configured in `.github/workflows/deploy.yml`

3. **Deploy using GitHub Actions**:
   The deployment workflow is triggered automatically on pushes to the `main` branch. You can also trigger it manually:
   - Go to Actions tab in your repository
   - Select "Deploy to GitHub Pages" workflow
   - Click "Run workflow" and select the `main` branch

### GitHub Actions Workflow

The workflow file `.github/workflows/deploy.yml` handles the deployment:

```yaml
name: Deploy to GitHub Pages

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

jobs:
  deploy:
    name: Deploy to GitHub Pages
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
        with:
          fetch-depth: 0

      - name: Setup Node.js
        uses: actions/setup-node@v4
        with:
          node-version: 20
          cache: npm

      - name: Install dependencies
        run: npm ci

      - name: Build website
        run: npm run build

      # Popular action to deploy to GitHub Pages:
      - name: Deploy to GitHub Pages
        uses: peaceiris/actions-gh-pages@v4
        with:
          github_token: ${{ secrets.GITHUB_TOKEN }}
          publish_dir: ./build
          user_name: github-actions[bot]
          user_email: 41898282+github-actions[bot]@users.noreply.github.com
```

## Cloudflare Pages Deployment

### Prerequisites
- Cloudflare account
- Cloudflare Pages project created

### Deployment Steps

1. **Connect to Cloudflare Pages**:
   - Log in to Cloudflare Dashboard
   - Navigate to Pages
   - Click "Create a project"
   - Connect your GitHub repository

2. **Configure Build Settings**:
   - Build command: `npm run build`
   - Build output directory: `build`
   - Root directory: `.` (root)

3. **Environment Variables** (if needed):
   - NODE_VERSION: `20`

4. **Deploy**:
   - Save the configuration
   - Cloudflare will automatically deploy from the `main` branch
   - Subsequent commits will trigger automatic deployments

### Manual Deployment (Alternative)

If you prefer to build and deploy manually:

1. **Build the site locally**:
   ```bash
   # Install dependencies
   npm install

   # Build the static site
   npm run build
   ```

2. **Deploy the `build/` directory** to your preferred hosting service.

## Verification Steps

After deployment:

1. **Check the live site** for proper rendering
2. **Verify navigation** works correctly across all modules
3. **Test code examples** and ensure they display properly
4. **Confirm responsive design** on different screen sizes
5. **Validate search functionality** if Algolia is configured

## Troubleshooting

### Common Issues:

- **Build failures**: Check that all MDX files have correct syntax
- **Missing assets**: Verify image paths are correct in deployed version
- **Navigation issues**: Confirm sidebar configuration is correct
- **Search not working**: Algolia configuration may need adjustment

### Build Logs:
Check GitHub Actions logs or Cloudflare Pages build logs for detailed error information.

## Post-Deployment Tasks

1. **Update documentation links** in the repository
2. **Share the deployment URL** with stakeholders
3. **Monitor site performance** and fix any rendering issues
4. **Set up custom domain** if needed (in GitHub Pages or Cloudflare settings)

## Rollback Procedure

If deployment issues occur:
1. Identify the problematic commit
2. Create a hotfix branch from the last known good state
3. Cherry-pick or revert problematic changes
4. Deploy the fix