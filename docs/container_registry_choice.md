# ADR: Container Registry Selection for Billify

## Status
Proposed

## Context
The Billify project requires a container registry to store Docker images for the backend and frontend components. We need a solution that provides:

1. Private repositories for our Docker images (at least 2: backend and frontend)
2. Cost-effective storage and distribution of container images
3. Integration with our development workflow and CI/CD pipeline
4. Suitable access controls and security features

We evaluated two primary options: GitHub Container Registry (GHCR) and DockerHub.

## Decision
Use GitHub Container Registry (GHCR) for Billify's container registry needs.

## Rationale

### GitHub Container Registry

#### Strengths
1. **GitHub Integration**
   - Seamless integration with GitHub repositories, issues, and workflows
   - Uses the same authentication as GitHub, simplifying access management
   - Native integration with GitHub Actions for automated builds and deployments

2. **Storage and Cost**
   - Free tier includes unlimited private repositories with 2GB storage, 10GB bandwidth/month
   - Sufficient for our MVP phase requirements (two private repositories)

3. **Security and Access Control**
   - Fine-grained permissions based on GitHub's team structure
   - Built-in vulnerability scanning through Dependabot
   - Granular package visibility controls (public, private, internal)

4. **Developer Experience**
   - Consolidated services reducing the number of separate accounts to manage
   - OCI compliance ensuring compatibility with various container tools

#### Limitations
1. **Maturity** - Relatively newer service compared to DockerHub (launched in 2020)
2. **Community Ecosystem** - Smaller ecosystem compared to DockerHub
3. **External CI/CD Integration** - May require additional configuration for non-GitHub CI/CD systems

### DockerHub

#### Strengths
1. **Market Leadership**
   - Well-established platform with proven reliability
   - Large ecosystem and community adoption
   - Most developers are already familiar with the platform

2. **Docker Integration**
   - Native integration with Docker CLI
   - Intuitive UI for exploring container images
   - Access to Docker Official Images and certified content

3. **Distribution Network**
   - Mature global CDN for faster pulls worldwide
   - Well-integrated with the broader Docker ecosystem

#### Limitations
1. **Free Tier Restrictions**
   - Only one free private repository (we need two)
   - Paid plans start at $5/month for Pro (unlimited private repositories)
   - More restrictive pull rate limits (anonymous: 100 pulls/6hrs, authenticated: 200 pulls/6hrs)

2. **Cost Structure**
   - Would require a paid plan ($5/month minimum) for our needs
   - Team Plan ($7/user/month) for team management features

3. **Security Features**
   - Advanced security scanning requires paid plans
   - Separate authentication system from code repository

### Project Compatibility Considerations

1. **Development Workflow**
   - Our codebase is hosted on GitHub, making GHCR a more integrated experience
   - CI/CD pipelines can be streamlined with GitHub Actions integration

2. **Cost Efficiency**
   - GHCR's free tier supports our need for two private repositories
   - As a startup, minimizing costs while maintaining quality is important

3. **Security Requirements**
   - The integrated vulnerability scanning in GHCR is valuable for a fintech application
   - Simplified access management through GitHub's existing permission system

4. **Future Scalability**
   - Both platforms scale well, but GitHub's higher free tier limits benefit our startup phase
   - GHCR scales naturally with GitHub's team and organization features

## Consequences

### Positive
1. **Cost Savings**
   - Free tier of GHCR meets our needs without additional costs
   - Avoids the $5/month minimum for DockerHub Pro

2. **Workflow Integration**
   - Streamlined development workflow with GitHub integration
   - Simplified CI/CD pipeline configuration with GitHub Actions

3. **Security Enhancements**
   - Built-in container vulnerability scanning without additional cost
   - Consistent access control through GitHub's permission system

### Considerations
1. **Learning Curve**
   - Team may need to adjust to GHCR workflows if more familiar with DockerHub
   - Documentation and community resources may be less extensive than DockerHub

2. **Vendor Lock-in**
   - Increasing dependency on GitHub ecosystem
   - Should maintain container portability to avoid lock-in

## Migration Path
If future requirements change, we can:
1. Push our images to multiple registries simultaneously
2. Implement registry-agnostic CI/CD pipelines
3. Evaluate self-hosted options (like Harbor) for greater control 