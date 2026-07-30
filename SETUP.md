# Environment Setup

How to get a local Saleor instance running so you can execute tests against it.

**Read the whole Windows section before starting.** Several steps fail silently in
ways that are hard to diagnose after the fact.

Budget 45–90 minutes for a first-time setup, most of it waiting on downloads.

---

## What you're setting up

Three separate directories. Only one of them is our repository.

```
~/
├── saleor-platform/        # Docker environment (cloned from upstream, not committed)
├── saleor-core/            # Saleor source code, for code review (not committed)
└── storefront-test-suite/  # OUR REPO — tests, evidence, report artifacts
```

Do not clone `saleor-platform` or `saleor-core` inside our repo. They are upstream
code; we only pin the version we tested against.

---

## Do you actually need all of this?

| Your role | What you need |
|---|---|
| Automation | Full setup — Docker + running instance |
| Exploratory testing | Full setup, or access to someone else's instance |
| Code review / static testing | `saleor-core` clone + a linter. **No Docker required.** |
| Test case design / report | Access to a running instance during working sessions |

If you're only doing code review or static analysis, skip to
[Code review setup](#code-review-setup-no-docker) at the bottom.

---

## Version we are testing

| Component | Version |
|---|---|
| Saleor Core (API) | `3.23` |
| Saleor Dashboard | `3.23` |
| PostgreSQL | `15-alpine` |
| Valkey (cache) | `8.1-alpine` |

Confirm your `saleor-platform/docker-compose.yml` shows `ghcr.io/saleor/saleor:3.23`.
If upstream has moved on and you get a different version, tell the group before
continuing — mismatched versions mean our test results won't be comparable, and our
report claims a specific version under test.

---

## Requirements

- Docker with Compose v2 (`docker compose`, with a space — not `docker-compose`)
- Git
- ~15 GB free disk
- ~6 GB RAM available to Docker

---

## Windows setup

The path of least resistance is WSL 2 + Docker Desktop. Order matters.

### 1. Install WSL 2 and a Linux distribution

Open PowerShell **as Administrator**:

```powershell
wsl --install
```

Reboot when prompted.

> **Gotcha:** on some Windows builds, `wsl --install` enables the WSL platform but
> installs no distribution. If you later see *"Windows Subsystem for Linux has no
> installed distributions"*, run:
>
> ```powershell
> wsl --install -d Ubuntu
> ```

On first launch Ubuntu asks for a UNIX username and password. These are separate from
your Windows login. The password is invisible as you type — that's normal, not a
frozen prompt.

### 2. Confirm you are on WSL **2**, not WSL 1

```powershell
wsl -l -v
```

`VERSION` must read `2`. If it reads `1`:

```powershell
wsl --set-version Ubuntu 2
wsl --set-default-version 2
```

The conversion takes a few minutes. Don't close the window.

> **Why this matters:** Docker Desktop cannot use WSL 1 distros and filters them out
> of its integration list entirely. The symptom is Docker reporting *"You don't have
> any WSL 2 distros installed"* while `wsl -l -v` clearly shows Ubuntu — because it's
> version 1.

### 3. Install Docker Desktop

Download from <https://www.docker.com/products/docker-desktop/>.

> **Gotcha — this one cost us hours:** right-click the installer and
> **Run as administrator**. A non-elevated install can appear to succeed while
> skipping the PATH entry and the WSL backend provisioning. The symptom is
> `docker: command not found` in both PowerShell and Ubuntu, with
> `C:\Program Files\Docker\Docker\resources\bin\docker.exe` missing entirely.

Keep "Use WSL 2 instead of Hyper-V" checked. Reboot after installing.

### 4. Enable WSL integration

Launch Docker Desktop and wait for the tray whale to stop animating.

Settings → Resources → **WSL Integration**:
- Enable integration with the default WSL distro
- Toggle **Ubuntu** on explicitly in the list below

Apply & Restart.

Sanity check in PowerShell — `wsl -l -v` should now show a `docker-desktop` entry
alongside Ubuntu. If it doesn't, the backend never provisioned and the integration
won't work no matter what the toggles say.

### 5. Check memory

There is **no memory slider** in Docker Desktop on the WSL 2 backend — Windows manages
it. Check what you actually have from inside Ubuntu:

```bash
free -h
```

If `total` is 6 GB or more, you're fine. If it's less, create `.wslconfig` in your
Windows user folder (PowerShell: `notepad "$env:USERPROFILE\.wslconfig"`):

```ini
[wsl2]
memory=8GB
processors=4
```

Then `wsl --shutdown`, quit Docker Desktop from the tray, and relaunch.

Don't set `memory` above about half your physical RAM or Windows itself starts
swapping. On an 8 GB machine, use `5GB` and close your browser while containers run.

### 6. Verify

Open a **new** Ubuntu terminal (Start menu → type `Ubuntu`). The `docker` binary is
only injected into shells opened *after* integration was enabled — an existing window
will never see it.

```bash
docker --version
docker compose version
docker run --rm hello-world
```

### Alternative: skip Docker Desktop entirely

If Docker Desktop keeps failing, install Docker Engine directly inside Ubuntu. Fully
supported and arguably simpler. See the Linux section below, then enable systemd by
adding this to `/etc/wsl.conf`:

```ini
[boot]
systemd=true
```

Run `wsl --shutdown` from PowerShell afterwards.

---

## macOS setup

1. Install Docker Desktop — check whether you need the Apple Silicon or Intel build.
2. Settings → Resources → Memory: at least 6 GB.
3. Settings → Resources → File Sharing: include the parent directory you'll clone into.
4. Apply & Restart, then verify with `docker run --rm hello-world`.

---

## Linux setup

```bash
sudo apt-get update
sudo apt-get install -y ca-certificates curl
sudo install -m 0755 -d /etc/apt/keyrings
sudo curl -fsSL https://download.docker.com/linux/ubuntu/gpg -o /etc/apt/keyrings/docker.asc
sudo chmod a+r /etc/apt/keyrings/docker.asc

echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.asc] https://download.docker.com/linux/ubuntu $(. /etc/os-release && echo "$VERSION_CODENAME") stable" | \
  sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

sudo apt-get update
sudo apt-get install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin

sudo usermod -aG docker $USER
newgrp docker
```

Verify with `docker run --rm hello-world`.

---

## Running Saleor

**On WSL, work in your Linux home directory, not `/mnt/c/`.** Cloning onto the Windows
filesystem is dramatically slower with a codebase this size.

```bash
cd ~
pwd    # should print /home/<your-username>
```

### 1. Clone

```bash
git clone https://github.com/saleor/saleor-platform.git
cd saleor-platform
```

### 2. Migrate

First heavy step — pulls several GB of images before running anything. Expect 10–20
minutes with long stretches of no visible output. Close your browser while it runs.

```bash
docker compose run --rm api python3 manage.py migrate
```

### 3. Seed the database

```bash
docker compose run --rm api python3 manage.py populatedb --createsuperuser
```

Creates sample products, customers, and orders, plus an admin account:

```
Email:    admin@example.com
Password: admin
```

### 4. Start

```bash
docker compose up
```

Leave this terminal running — it streams logs from every container, which is genuinely
useful when something misbehaves. `Ctrl+C` stops everything.

---

## Verify it works

| Service | URL | Check |
|---|---|---|
| Dashboard | <http://localhost:9000> | Log in as admin, see seeded products |
| GraphQL API | <http://localhost:8000/graphql/> | Playground loads |
| Mailpit | <http://localhost:8025> | Inbox UI loads |
| Jaeger | <http://localhost:16686> | Trace UI loads |

Mailpit captures all outbound email, which is what makes password reset and order
confirmation testable end to end.

---

## Record this for the report

Section 8.1 of the Word report needs your environment details. Capture them now rather
than reconstructing them in week six:

```bash
docker --version
docker compose version
free -h
```

Plus your OS and version, and your browser and version. Add them to
`/evidence/environments.md` in our repo.

If group members are on different operating systems, note it — that's a real
compatibility data point for the non-functional testing section, not just admin.

---

## Everyday commands

```bash
docker compose up                                  # start everything
docker compose up api worker                       # backend only, lighter
docker compose logs -f api                         # tail API logs
docker compose exec api python manage.py shell     # Django shell
docker compose stop                                # stop, keep data
docker compose down --volumes db                   # wipe DB and reseed from scratch
```

After `down --volumes db` you must re-run the migrate and populatedb steps.

Use it to reset to a known-clean state between test runs — our test cases assume the
seeded dataset, so a polluted database causes confusing failures.

---

## Code review setup (no Docker)

For static testing and code review, all you need is the source:

```bash
cd ~
git clone --branch 3.23 https://github.com/saleor/saleor.git saleor-core
```

Match the branch to the image version above so your findings describe the code we're
actually running. Reviewing `main` while everyone else tests `3.23` produces findings
that don't line up with the rest of the report.

Ruff is Saleor's own linter and a reasonable starting point:

```bash
pip install ruff
cd saleor-core
ruff check saleor/ > ~/storefront-test-suite/evidence/ruff-output.txt
```

---

## Troubleshooting

| Symptom | Cause | Fix |
|---|---|---|
| `WSL has no installed distributions` | Platform enabled, no distro | `wsl --install -d Ubuntu` |
| Docker: *"no WSL 2 distros installed"* but `wsl -l -v` shows Ubuntu | Ubuntu is WSL **1** | `wsl --set-version Ubuntu 2` |
| `docker: command not found` in PowerShell **and** Ubuntu | Install was not elevated | Uninstall, reboot, reinstall as administrator |
| `docker: command not found` in Ubuntu only | Integration off, or stale shell | Enable Ubuntu in WSL Integration, open a **new** terminal |
| No `docker-desktop` in `wsl -l -v` | Backend never provisioned | Quit Docker Desktop from tray, `wsl --shutdown`, relaunch |
| No memory slider in Docker settings | Normal on WSL 2 backend | Use `.wslconfig` |
| `net localgroup docker-users` → error 1376 | Group not used on this configuration | Ignore — not the problem |
| API container dies during `migrate` | Out of memory | Raise WSL memory, close browser, retry |
| Port already in use | Something on 8000/9000/5432 | `docker compose down`, or stop the conflicting service |
| Builds fail, no disk space | Docker cache | `docker system prune` (removes stopped containers and dangling images) |

---

## Getting help

If you're stuck for more than 30 minutes, post in the group chat with:
- the exact command you ran
- the full error text (not a screenshot — we may need to search it)
- your OS and `docker --version`

Setup problems are shared infrastructure, not individual failures. One person solving
it twice is a waste; add anything new you hit to the table above.
