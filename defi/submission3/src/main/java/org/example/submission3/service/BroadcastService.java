package org.example.submission3.service;

import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.example.submission3.client.BroadcastClient;
import org.example.submission3.dto.BroadcastRequest;
import org.example.submission3.utils.ObjectMapperUtils;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Service;

@Slf4j
@Service
@RequiredArgsConstructor
public class BroadcastService {

    private final NodeService nodeService;

    private final BroadcastClient broadcastClient;

    private final CryptoService cryptoService;

    @Value("${peer-to-peer.broadcast.address}")
    private String broadcastAddress;

    @Value("${peer-to-peer.broadcast.port}")
    private int broadcastPort;

    @Value("${peer-to-peer.tcp-port}")
    private int tcpPort;

    public void broadcast() {
        var nodeId = nodeService.getCurrentNodeId();
        var request = BroadcastRequest.builder()
                .nodeId(nodeId)
                .tcpPort(tcpPort)
                .publicKey(cryptoService.getPublicKeyBase64())
                .build();
        log.info("BroadcastService: Broadcasting nodeId=[{}] on port [{}] with public key [{}]",
                nodeId, tcpPort, cryptoService.getPublicKeyBase64());
        broadcastClient.sendBroadcastRequest(ObjectMapperUtils.serialize(request), broadcastAddress, broadcastPort);
    }
}
