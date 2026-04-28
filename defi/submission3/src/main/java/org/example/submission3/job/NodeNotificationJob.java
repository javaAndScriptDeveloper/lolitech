package org.example.submission3.job;

import lombok.RequiredArgsConstructor;
import org.example.submission3.service.NodeNotificationService;
import org.springframework.scheduling.annotation.Scheduled;
import org.springframework.stereotype.Component;

@Component
@RequiredArgsConstructor
public class NodeNotificationJob {

    private final NodeNotificationService nodeNotificationService;

    @Scheduled(fixedRateString = "${peer-to-peer.notification.rate}")
    public void notifyNodes() {
        nodeNotificationService.notifyNodes();
    }
}
