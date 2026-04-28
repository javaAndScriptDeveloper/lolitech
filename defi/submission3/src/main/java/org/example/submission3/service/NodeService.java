package org.example.submission3.service;

import org.example.submission3.model.Node;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Service;

import java.net.InetSocketAddress;
import java.util.ArrayList;
import java.util.List;
import java.util.UUID;
import java.util.concurrent.ConcurrentHashMap;

@Service
public class NodeService {

    @Value("${peer-to-peer.node-id}")
    private String nodeId;

    private final List<Node> nodes = new ArrayList<>();

    public String getCurrentNodeId() {
        return nodeId;
    }

    public void add(Node node) {
        if (node.getId().equals(nodeId)) {
            return;
        }
        if (nodes.stream().noneMatch(n -> n.getId().equals(node.getId()))) {
            nodes.add(node);
        }
    }

    public List<Node> getNodes() {
        return new ArrayList<>(nodes);
    }

}
