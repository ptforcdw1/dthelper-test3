# PetClinic Setup Notes

## Setup Steps

1. **Confirmed Docker Desktop was running** (v29.4.2) via `docker info`.

2. **Created `petclinic/docker-compose.yml`** mapping host port `8090` to container port `8080`.

3. **Attempted to use a pre-built image** (`springcommunity/spring-petclinic:latest`) — not found on Docker Hub.

4. **Attempted to download a pre-built JAR** from GitHub Releases — no releases are published for the spring-petclinic project.

5. **Created `petclinic/Dockerfile`** using a multi-stage build:
   - Stage 1 (`maven:3.9-eclipse-temurin-21-alpine`): installs git, clones the official repo from `https://github.com/spring-projects/spring-petclinic.git`, and builds with `mvn package -DskipTests`.
   - Stage 2 (`eclipse-temurin:21-jre-alpine`): copies the built JAR into a slim JRE image and sets the entrypoint.

6. **Built the image** with `docker compose build` — tagged as `petclinic:local`.

7. **Started the container** with `docker compose up -d` — container name `petclinic`, port `8090:8080`.

8. **Verified** the app responds at `http://localhost:8090` (HTTP 200).

---

## Useful Commands

```powershell
# Start the container (detached)
docker compose -f petclinic/docker-compose.yml up -d

# Stop and remove the container
docker compose -f petclinic/docker-compose.yml down

# Rebuild the image (e.g. after Dockerfile changes)
docker compose -f petclinic/docker-compose.yml build

# Rebuild and restart in one step
docker compose -f petclinic/docker-compose.yml up -d --build

# Stream logs
docker logs petclinic -f

# Check container status and port mapping
docker ps --filter "name=petclinic" --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"
```

**App URL:** http://localhost:8090
