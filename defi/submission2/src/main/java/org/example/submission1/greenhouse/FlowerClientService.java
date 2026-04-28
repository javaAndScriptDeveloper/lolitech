package org.example.submission1.greenhouse;

import io.grpc.stub.StreamObserver;
import lombok.extern.slf4j.Slf4j;
import net.devh.boot.grpc.client.inject.GrpcClient;
import org.example.submission1.Empty;
import org.example.submission1.FlowerRegistrationServiceGrpc;
import org.example.submission1.RegisterFlowerMessage;
import org.springframework.amqp.rabbit.core.RabbitTemplate;
import org.springframework.boot.context.event.ApplicationReadyEvent;
import org.springframework.context.event.EventListener;
import org.springframework.stereotype.Service;

@Slf4j
@Service
public class FlowerClientService {

    @GrpcClient("flower-service")
    private FlowerRegistrationServiceGrpc.FlowerRegistrationServiceStub flowerStub;

    private final RabbitTemplate rabbitTemplate;

    public FlowerClientService(RabbitTemplate rabbitTemplate) {
        this.rabbitTemplate = rabbitTemplate;
    }

    @EventListener(ApplicationReadyEvent.class)
    public void subscribe() {
        log.info("Subscribing to gRPC flower stream");
        flowerStub.subscribeMessages(Empty.getDefaultInstance(), new StreamObserver<>() {
            @Override
            public void onNext(RegisterFlowerMessage message) {
                log.debug("Received flower via gRPC: name={}, origin={}", message.getName(), message.getOrigin());
                rabbitTemplate.convertAndSend(RabbitConfiguration.TOPIC_EXCHANGE_NAME, "flower.register", message);
                log.info("Forwarded flower to RabbitMQ: name={}", message.getName());
            }

            @Override
            public void onError(Throwable t) {
                log.error("gRPC stream error: {}", t.getMessage(), t);
            }

            @Override
            public void onCompleted() {
                log.info("gRPC stream completed");
            }
        });
    }
}
