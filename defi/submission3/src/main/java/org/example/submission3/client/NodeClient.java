package org.example.submission3.client;

import org.example.submission3.dto.NodeNotificationRequest;
import org.springframework.cloud.openfeign.FeignClient;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;

import java.net.URI;

@FeignClient(name = "node-client", url = "http://localhost")
public interface NodeClient {

    @PostMapping("/api/messages")
    void send(URI baseUrl, @RequestBody NodeNotificationRequest request);

}
