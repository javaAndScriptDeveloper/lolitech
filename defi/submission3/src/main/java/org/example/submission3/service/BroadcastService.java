package org.example.submission3.service;

import lombok.RequiredArgsConstructor;
import org.example.submission3.client.BroadcastClient;
import org.example.submission3.dto.BroadcastRequest;
import org.example.submission3.utils.ObjectMapperUtils;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Service;

@Service
@RequiredArgsConstructor
public class BroadcastService {

    private final NodeService nodeService;

    private final BroadcastClient broadcastClient;

    @Value("${peer-to-peer.broadcast.address}")
    private String broadcastAddress;

    @Value("${peer-to-peer.broadcast.port}")
    private int broadcastPort;

    @Value("${peer-to-peer.tcp-port}")
    private int tcpPort;

    public void broadcast() {
        var request = BroadcastRequest.builder()
                .nodeId(nodeService.getCurrentNodeId())
                .tcpPort(tcpPort)
                        .build();
        broadcastClient.sendBroadcastRequest(ObjectMapperUtils.serialize(request), broadcastAddress, broadcastPort);
    }
}
