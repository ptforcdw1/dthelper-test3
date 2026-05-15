# Stage 1: Build the Spring Boot app
FROM maven:3.9-eclipse-temurin-21-alpine AS build
WORKDIR /build
RUN apk add --no-cache git && \
    git clone --depth 1 https://github.com/spring-projects/spring-petclinic.git . && \
    mvn package -q -DskipTests

# Stage 2: Download Dynatrace OneAgent PaaS package (Java only)
FROM alpine:3.20 AS oneagent
ARG DT_TENANT_URL=https://ylq89164.live.dynatrace.com
ARG DT_PAAS_TOKEN
RUN apk add --no-cache curl unzip && \
    mkdir -p /opt/dynatrace/oneagent && \
    curl -fsSL \
      "${DT_TENANT_URL}/api/v1/deployment/installer/agent/unix/paas/latest?include=java&bitness=64" \
      -H "Authorization: Api-Token ${DT_PAAS_TOKEN}" \
      -o /tmp/oneagent.zip && \
    unzip -q /tmp/oneagent.zip -d /opt/dynatrace/oneagent

# Stage 3: Final runtime image
FROM eclipse-temurin:21-jre-alpine
WORKDIR /app
COPY --from=build /build/target/spring-petclinic-*.jar app.jar
COPY --from=oneagent /opt/dynatrace/oneagent /opt/dynatrace/oneagent
ENV JAVA_TOOL_OPTIONS="-agentpath:/opt/dynatrace/oneagent/agent/lib64/liboneagentproc.so"
EXPOSE 8080
ENTRYPOINT ["java", "-jar", "app.jar"]
