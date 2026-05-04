package org.example.submission3.service;

import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.example.submission3.client.NodeClient;
import org.example.submission3.dto.NodeNotificationRequest;
import org.example.submission3.model.Node;
import org.springframework.stereotype.Service;

import java.net.URI;

@Slf4j
@Service
@RequiredArgsConstructor
public class NodeNotificationService {

    private static final String NOTIFICATION_TEMPLATE = "Greeting node [%s] from node [%s] !";

    private final NodeService nodeService;

    private final NodeClient nodeClient;

    private final CryptoService cryptoService;

    public void notifyNodes() {
        nodeService.getNodes()
                .forEach(this::notifyNode);
    }

    private void notifyNode(Node node) {
        var uri       = URI.create("http://" + node.getAddress().getAddress().getHostAddress() + ":" + node.getAddress().getPort());
        var senderId  = nodeService.getCurrentNodeId();
        var message   = NOTIFICATION_TEMPLATE.formatted(node.getId(), senderId);
        var timestamp = System.currentTimeMillis();
        var payload   = senderId + ":" + message + ":" + timestamp;
        var signature = cryptoService.sign(payload);
        log.info("NodeNotificationService: Sending signed notification to node [{}]. Payload: [{}]", node.getId(), payload);
        var request = NodeNotificationRequest.builder()
                .message(message)
                .senderId(senderId)
                .timestamp(timestamp)
                .signature(signature)
                .build();
        nodeClient.send(uri, request);
    }

}
