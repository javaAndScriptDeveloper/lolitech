package org.example.submission3.controller;

import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.example.submission3.dto.NodeNotificationRequest;
import org.example.submission3.exception.SignatureVerificationException;
import org.example.submission3.service.CryptoService;
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

    private static final long TIMESTAMP_TOLERANCE_MS = 30_000L;

    private final NodeService nodeService;

    private final CryptoService cryptoService;

    @PostMapping
    public void receiveNotification(@RequestBody NodeNotificationRequest request) {
        var currentNodeId = nodeService.getCurrentNodeId();
        log.info("NodeController: Node [{}] received notification from sender [{}]", currentNodeId, request.getSenderId());

        var skew = Math.abs(System.currentTimeMillis() - request.getTimestamp());
        if (skew > TIMESTAMP_TOLERANCE_MS) {
            log.error("NodeController: Timestamp rejected for sender [{}]. Skew: {}ms", request.getSenderId(), skew);
            throw new SignatureVerificationException("Timestamp out of allowed window for sender: " + request.getSenderId());
        }

        var senderNode = nodeService.findById(request.getSenderId())
                .orElseThrow(() -> {
                    log.error("NodeController: Unknown sender [{}]", request.getSenderId());
                    return new SignatureVerificationException("Unknown sender: " + request.getSenderId());
                });

        var payload = request.getSenderId() + ":" + request.getMessage() + ":" + request.getTimestamp();
        var valid   = cryptoService.verify(payload, request.getSignature(), senderNode.getPublicKey());
        if (!valid) {
            log.error("NodeController: Signature verification FAILED for sender [{}]", request.getSenderId());
            throw new SignatureVerificationException("Invalid signature from sender: " + request.getSenderId());
        }

        log.info("NodeController: Signature OK for sender [{}]. Message: {}", request.getSenderId(), request.getMessage());
        log.info("Node [{}] received message: {}", currentNodeId, request.getMessage());
    }
}
