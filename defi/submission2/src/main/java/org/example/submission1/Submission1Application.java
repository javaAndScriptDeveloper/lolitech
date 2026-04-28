package org.example.submission1;

import org.example.submission1.FlowerRegistrationServiceGrpc;
import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;
import org.springframework.retry.annotation.EnableRetry;
import org.springframework.scheduling.annotation.EnableScheduling;

@EnableRetry
@EnableScheduling
@SpringBootApplication
public class Submission1Application {

    public static void main(String[] args) {
        SpringApplication.run(Submission1Application.class, args);
    }

}
