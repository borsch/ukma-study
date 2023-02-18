package com.github.borsch.hrsystem;

import org.springframework.boot.test.context.TestConfiguration;
import org.springframework.test.context.DynamicPropertyRegistry;
import org.springframework.test.context.DynamicPropertySource;
import org.testcontainers.containers.Neo4jContainer;
import org.testcontainers.containers.Neo4jLabsPlugin;

@TestConfiguration
public abstract class EmbeddedNeo4jConfig {

    private static final Neo4jContainer<?> neo4j = new Neo4jContainer<>("neo4j:4.4")
        .withLabsPlugins(Neo4jLabsPlugin.APOC)
        .withReuse(true);

    @DynamicPropertySource
    static void neo4jProperties(DynamicPropertyRegistry registry) {

        neo4j.start();

        registry.add("spring.neo4j.uri", neo4j::getBoltUrl);
        registry.add("spring.neo4j.authentication.username", () -> "neo4j");
        registry.add("spring.neo4j.authentication.password", neo4j::getAdminPassword);
    }
}