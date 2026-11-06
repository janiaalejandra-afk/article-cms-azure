# Write-up

### Analyze, choose, and justify the appropriate resource option for deploying the app.

The Article CMS is a small Flask web app. It stores article data in Azure SQL Database and images in Azure Blob Storage, and it signs users in with Microsoft Entra ID (MSAL). The app itself is stateless apart from the server-side session, so it can run on either an **Azure Virtual Machine (IaaS)** or **Azure App Service (PaaS)**.

| Criteria | Virtual Machine (IaaS) | App Service (PaaS) |
|---|---|---|
| **Costs** | You pay for the VM size (CPU/RAM) for every hour it is running, whether it gets traffic or not. You also pay for the OS disk, public IP and bandwidth. The cheapest size (B1ls) costs a few dollars a month, but it has very little memory. There is also an operational cost: someone has to install, patch and maintain the OS, Python, the ODBC driver, Nginx and the TLS certificates. | You pay for the App Service Plan tier. The **Free (F1)** tier costs $0, and the Basic tier (B1) has a predictable monthly price. The OS, runtime, load balancer and TLS for `*.azurewebsites.net` are included, so there is almost no maintenance cost. Several apps can share the same plan. |
| **Scalability** | To scale vertically, you resize the VM, which requires a restart. To scale horizontally, you must set up a VM Scale Set, a load balancer and a way to deploy the code to every instance. This gives a lot of flexibility, but it takes manual work. | Built-in vertical scaling (change the tier) and horizontal scale-out (manual or autoscale rules on Standard+ tiers) with a click. A load balancer is included. The limits are the maximums of each tier, and you cannot pick custom hardware. |
| **Availability** | A single VM has an SLA only with Premium SSD disks. For high availability you need Availability Sets/Zones, several VMs and a load balancer, and you must configure and monitor all of them yourself. Health checks and restarts after a crash also depend on you (for example, systemd). | Paid tiers have a 99.95% SLA. The platform restarts unhealthy instances and handles OS and runtime patches. Deployment slots (Standard+) allow zero-downtime swaps. The Free tier has no SLA and has daily CPU quotas, which is acceptable for a demo or development. |
| **Workflow** | Manual or scripted setup: SSH in, install packages, clone the repo, create a virtualenv, configure Nginx as a reverse proxy, create a self-signed certificate, and keep the process running. Each new deployment means pulling the code and restarting it. You have full control (root access, any OS package, any port). | Connect the GitHub repo in the Deployment Center. Every push to `main` builds and deploys the app automatically through GitHub Actions or Oryx. Secrets are stored as App Settings (environment variables), and logs are available in the **Log stream** without extra setup. You have less control over the OS, because only the supported runtimes and ports 80/443 are available. |

**Choice: Azure App Service.**

**Justification:** The CMS is a standard Python/Flask web app. It does not need custom OS packages, special ports, or background processes. The App Service Python image already includes the Microsoft ODBC driver for SQL Server, so the managed platform covers everything the app needs. App Service is the cheaper option here (Free/Basic tier and no OS maintenance). It also gives built-in HTTPS on `azurewebsites.net`, which Microsoft Entra ID requires for the redirect URI. Continuous deployment from GitHub, App Settings for secrets, and the built-in Log stream speed up the development workflow. They also make it easy to show the login logs that this project asks for. Scaling up or out later only means changing the plan, with no changes to the app.

### Assess app changes that would change your decision.

I would switch to a **Virtual Machine** if the app needed more control over the infrastructure than App Service allows. For example:

- The app needs OS-level dependencies or system software that the App Service runtime images do not support. Examples: a specific ODBC/driver version, image-processing libraries, GPU drivers, or a self-hosted database or cache on the same machine.
- The app needs non-HTTP protocols, custom ports, long-running background workers or daemons, or access to the file system that must persist and be shared beyond what App Service provides.
- The app has to run on a specific OS version or a hardened image, or it needs root access for compliance and security agents, custom networking or a custom TLS termination.
- Traffic is constant and high enough that reserved VM instances (or a VM Scale Set) are cheaper than equivalent Premium App Service plans, and the team has the operations skills to maintain them.

If I moved to a VM, I would also need to:

- Provision Nginx as a reverse proxy and a real TLS certificate (for example, Let's Encrypt with a DNS name), because Entra ID needs an HTTPS redirect URI.
- Run the app with Gunicorn under systemd so it restarts automatically.
- Install `msodbcsql`.
- Open the NSG ports (22/80/443).
- Store secrets as environment variables or in Key Vault.
- Ship logs to Azure Monitor or Log Analytics.
- Add a load balancer and Availability Zones or a Scale Set for high availability.
