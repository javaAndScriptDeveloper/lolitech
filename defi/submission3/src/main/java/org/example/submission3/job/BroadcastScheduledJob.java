package org.example.submission3.job;

import lombok.RequiredArgsConstructor;
import org.example.submission3.service.BroadcastService;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.scheduling.annotation.Scheduled;
import org.springframework.stereotype.Component;

@Component
@RequiredArgsConstructor
public class BroadcastScheduledJob {

    private final BroadcastService broadcastService;

    @Scheduled(fixedRateString = "${peer-to-peer.broadcast.rate}")
    public void broadcast() {
        broadcastService.broadcast();
    }

}
