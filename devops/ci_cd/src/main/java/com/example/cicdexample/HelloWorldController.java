package com.example.cicdexample;

import org.springframework.http.MediaType;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.ResponseBody;
import org.springframework.web.bind.annotation.RestController;

@RestController("/")
public class HelloWorldController {

    @GetMapping(produces = MediaType.APPLICATION_JSON_VALUE)
    @ResponseBody
    String helloWorld() {
        return "Hello world!!!!!";
    }
}
