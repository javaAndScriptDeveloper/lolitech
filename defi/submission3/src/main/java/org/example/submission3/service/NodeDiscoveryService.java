package org.example.submission3.service;

import lombok.RequiredArgsConstructor;
import lombok.SneakyThrows;
import lombok.extern.log4j.Log4j;
import lombok.extern.slf4j.Slf4j;
import org.example.submission3.dto.BroadcastRequest;
import org.example.submission3.model.Node;
import org.example.submission3.utils.ObjectMapperUtils;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.boot.context.event.ApplicationReadyEvent;
import org.springframework.context.event.EventListener;
import org.springframework.stereotype.Service;

import java.io.IOException;
import java.net.DatagramPacket;
import java.net.DatagramSocket;
import java.net.InetAddress;
import java.net.InetSocketAddress;

@Slf4j
@Service
@RequiredArgsConstructor
public class NodeDiscoveryService {

    private final NodeService nodeService;

    @Value("${peer-to-peer.broadcast.address}")
    private String broadcastAddress;

    @Value("${peer-to-peer.broadcast.port}")
    private int broadcastPort;

    @EventListener(ApplicationReadyEvent.class)
    public void runDiscoveryThread() {
        var discoveryThread = new Thread(this::discoverNodes);
        discoveryThread.setDaemon(true);
        discoveryThread.start();
    }

    @SneakyThrows
    private void discoverNodes() {
        try (var socket = new DatagramSocket(broadcastPort)) {
            
            var buffer = new byte[1024];

            while (!Thread.currentThread().isInterrupted()) {
                var packet = new DatagramPacket(buffer, buffer.length);

                socket.receive(packet);

                var rawBroadcastRequest = new String(packet.getData(), 0, packet.getLength());

                handleDiscoveredNode(rawBroadcastRequest, packet.getAddress());
            }
        } catch (IOException e) {
            log.error("Discovery thread error: " + e.getMessage());
        }   
    }

    private void handleDiscoveredNode(String rawBroadcastRequest, InetAddress inetAddress) {
        var broadcastRequest = ObjectMapperUtils.deserialize(rawBroadcastRequest, BroadcastRequest.class);
        var inetSocketAddress = new InetSocketAddress(inetAddress, broadcastRequest.getTcpPort());
        var node = Node.builder()
                .id(broadcastRequest.getNodeId())
                .address(inetSocketAddress)
                .publicKey(broadcastRequest.getPublicKey())
                .build();
        log.info("NodeDiscoveryService: Discovered node [{}] at [{}] with public key [{}]",
                node.getId(), inetSocketAddress, broadcastRequest.getPublicKey());
        nodeService.add(node);
    }
}
