import com.google.protobuf.gradle.id

plugins {
	java
	id("org.springframework.boot") version "3.3.5"
	id("io.spring.dependency-management") version "1.1.7"
	id("com.google.protobuf") version "0.9.4"
}

group = "org.example"
version = "0.0.1-SNAPSHOT"

java {
	toolchain {
		languageVersion = JavaLanguageVersion.of(21)
	}
}

repositories {
	mavenCentral()
}

// Force version alignment to avoid NoSuchMethodError
configurations.all {
	resolutionStrategy.eachDependency {
		if (requested.group == "com.google.protobuf") {
			useVersion("3.25.1")
		}
		if (requested.group == "io.grpc") {
			useVersion("1.63.0")
		}
	}
}

dependencies {
	// Web (required for H2 console)
	implementation("org.springframework.boot:spring-boot-starter-web")

	// RabbitMQ & Serialization
	implementation("org.springframework.boot:spring-boot-starter-amqp")
	implementation("com.hubspot.jackson:jackson-datatype-protobuf:0.9.15")
	implementation("com.fasterxml.jackson.core:jackson-databind")
	implementation("com.fasterxml.jackson.datatype:jackson-datatype-jsr310")

	// Fix for Java 21 @Generated annotation
	implementation("javax.annotation:javax.annotation-api:1.3.2")

	// STABLE gRPC Community Starters
	implementation("net.devh:grpc-client-spring-boot-starter:3.1.0.RELEASE")
	implementation("net.devh:grpc-server-spring-boot-starter:3.1.0.RELEASE")

	// Core gRPC and Protobuf (Matching protoc version)
	implementation("io.grpc:grpc-netty-shaded:1.63.0")
	implementation("io.grpc:grpc-protobuf:1.63.0")
	implementation("io.grpc:grpc-stub:1.63.0")
	implementation("com.google.protobuf:protobuf-java:3.25.1")
	implementation("io.grpc:grpc-services:1.63.0")

	// Persistence
	implementation("org.springframework.boot:spring-boot-starter-data-jpa")
	runtimeOnly("com.h2database:h2")

	// Utilities
	implementation("org.springframework.retry:spring-retry:2.0.12")
	implementation("org.springframework:spring-aspects")

	compileOnly("org.projectlombok:lombok")
	annotationProcessor("org.projectlombok:lombok")
	testImplementation("org.springframework.boot:spring-boot-starter-test")
}

// The spring-grpc-dependencies BOM is no longer needed with devh starters
// You can remove the dependencyManagement block entirely

protobuf {
	protoc {
		artifact = "com.google.protobuf:protoc:3.25.1"
	}
	plugins {
		id("grpc") {
			artifact = "io.grpc:protoc-gen-grpc-java:1.63.0"
		}
	}
	generateProtoTasks {
		all().forEach {
			it.plugins {
				id("grpc") {
					option("@generated=omit")
				}
			}
		}
	}
}