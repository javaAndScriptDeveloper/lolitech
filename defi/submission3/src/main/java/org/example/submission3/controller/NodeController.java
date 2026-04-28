package org.example.submission3.controller;

import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.example.submission3.dto.NodeNotificationRequest;
import org.example.submission3.service.NodeService;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

@Slf4j
@RestController
@RequestMapping("/api/messages")
@RequiredArgsConstructor
public class NodeController {

    private final NodeService nodeService;

    @PostMapping
    public void receiveNotification(@RequestBody NodeNotificationRequest request) {
        log.info("Node [{}] received message: {}", nodeService.getCurrentNodeId(), request.getMessage());
    }
}
