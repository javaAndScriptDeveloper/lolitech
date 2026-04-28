package org.example.submission1;

import io.grpc.stub.StreamObserver;
import org.springframework.grpc.server.service.GrpcService;
import org.springframework.scheduling.annotation.Scheduled;

import java.time.LocalDateTime;
import java.util.concurrent.CopyOnWriteArraySet;

@GrpcService
public class NotificationServiceImpl extends NotificationServiceGrpc.NotificationServiceImplBase{

    private final CopyOnWriteArraySet<StreamObserver<ScheduledMessage>> clients = new CopyOnWriteArraySet<>();

    @Override
    public void subscribeMessages(Empty request, StreamObserver<ScheduledMessage> responseObserver) {
        // Add the new client to our broadcast list
        clients.add(responseObserver);

        // Logic to remove client if they disconnect
        if (responseObserver instanceof io.grpc.stub.ServerCallStreamObserver) {
            ((io.grpc.stub.ServerCallStreamObserver<ScheduledMessage>) responseObserver).setOnCancelHandler(() -> {
                clients.remove(responseObserver);
            });
        }
    }

    @Scheduled(fixedRate = 5000) // Runs every 5 seconds
    public void sendUpdates() {
        ScheduledMessage message = ScheduledMessage.newBuilder()
                .setContent("System Update")
                .setTimestamp(LocalDateTime.now().toString())
                .build();

        for (StreamObserver<ScheduledMessage> client : clients) {
            try {
                client.onNext(message);
            } catch (Exception e) {
                // Remove broken/closed connections
                clients.remove(client);
            }
        }
    }
}
