package org.example.submission3.service;

import lombok.RequiredArgsConstructor;
import org.example.submission3.client.NodeClient;
import org.example.submission3.dto.NodeNotificationRequest;
import org.example.submission3.model.Node;
import org.springframework.stereotype.Service;

import java.net.URI;

@Service
@RequiredArgsConstructor
public class NodeNotificationService {

    private static final String NOTIFICATION_TEMPLATE = "Greeting node [%s] from node [%s] !";

    private final NodeService nodeService;

    private final NodeClient nodeClient;

    public void notifyNodes() {
        nodeService.getNodes()
                .forEach(this::notifyNode);
    }

    private void notifyNode(Node node) {
        var uri = URI.create("http://" + node.getAddress().getAddress().getHostAddress() + ":" + node.getAddress().getPort());
        var message = NOTIFICATION_TEMPLATE.formatted(node.getId(), nodeService.getCurrentNodeId());
        var request = NodeNotificationRequest.builder()
                .message(message)
                .build();
        nodeClient.send(uri, request);
    }

}
