FROM quay.io/keycloak/keycloak:latest AS builder

# Configure build-time settings that get baked into the optimized image
ENV KC_DB=postgres
ENV KC_HEALTH_ENABLED=true
ENV KC_METRICS_ENABLED=true
ENV KC_HTTP_ENABLED=true
ENV KC_PROXY_HEADERS=xforwarded
ENV KC_HOSTNAME_STRICT_HTTPS=false

# Build the optimized Keycloak distribution
RUN /opt/keycloak/bin/kc.sh build

# --- Production stage ---
FROM quay.io/keycloak/keycloak:latest

# Copy the pre-built optimized config from the builder
COPY --from=builder /opt/keycloak/ /opt/keycloak/

ENTRYPOINT ["/opt/keycloak/bin/kc.sh"]
